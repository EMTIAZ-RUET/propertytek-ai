"""
LangGraph-based FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from src.workflows.graph import create_property_workflow
from src.workflows.state import WorkflowState
from src.models.schemas import ChatRequest, ChatResponse
from src.services.chat_history import ChatHistoryService
from src.services.search_session import SearchSessionService
from src.workflows.booking_flow import booking_flow_manager
from src.tools.calendar_tool import CalendarTool
from src.tools.sms_tool import SMSTool
from config.settings import settings
from src.visualization.workflow_visualizer import workflow_visualizer, NodeStatus

logger = logging.getLogger(__name__)

app = FastAPI(
    title="PropertyTek AI Chatbot",
    description="LangGraph-powered property management chatbot",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow = create_property_workflow()
chat_history = ChatHistoryService()
search_session = SearchSessionService()
calendar_tool = CalendarTool()
sms_tool = SMSTool()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "PropertyTek LangGraph API"}


@app.get("/visualization/workflow")
async def get_workflow_structure():
    """Get complete workflow structure and execution data"""
    return workflow_visualizer.get_workflow_structure()

@app.get("/visualization/live")
async def get_live_execution_data():
    """Get real-time execution data for live visualization updates"""
    return workflow_visualizer.get_current_execution_data()

@app.post("/visualization/clear")
async def clear_executions():
    """Clear all execution history"""
    workflow_visualizer.executions.clear()
    workflow_visualizer.current_execution = None
    return {"status": "cleared"}

@app.get("/visualization/current")
async def get_current_execution():
    """Get current execution data"""
    return workflow_visualizer.get_current_execution_data()

@app.get("/visualization/executions")
async def get_all_executions():
    """Get all execution history"""
    return {
        "executions": {exec_id: workflow_visualizer.executions[exec_id].__dict__ 
                      for exec_id in workflow_visualizer.executions}
    }

@app.get("/visualization", response_class=HTMLResponse)
async def visualization_frontend():
    """Serve the integrated visualization frontend"""
    from src.visualization.frontend import VISUALIZATION_HTML
    return HTMLResponse(content=VISUALIZATION_HTML)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Start workflow visualization tracking
        execution_id = await workflow_visualizer.start_execution(
            user_query=request.query,
            user_id=request.user_id
        )
        
        recent_messages = chat_history.get_last_messages(request.user_id, limit=10)

        # Load prior filters for this user and pass into state to enable cumulative filtering
        prior_filters = search_session.get_filters(request.user_id)

        initial_state: WorkflowState = {
            "user_query": request.query,
            "user_id": request.user_id,
            "conversation_history": request.conversation_history,
            "messages": recent_messages,
            "action_type": request.action_type,
            "property_id": request.property_id,
            "selected_slot": request.selected_slot,
            "user_info": request.user_info or {},
            "intent": None,
            "entities": {},
            "confidence": None,
            "properties": [],
            "search_filters": prior_filters or {},
            "search_query": None,
            "queries": [],
            "reflection_notes": None,
            "needs_more_research": None,
            "reflection_loops": 0,
            "available_slots": [],
            "appointment_details": None,
            "user_name": None,
            "user_email": None,
            "user_phone": None,
            "user_pets": None,
            "calendar_event_id": None,
            "sms_sent": None,
            "sms_result": None,
            "response_message": "",
            "suggested_actions": [],
            "current_step": "property_search",
            "requires_user_info": False,
            "property_details": None,
            "error": None,
            "next_step": None,
            "workflow_complete": False,
            # iterative helpers
            "next_field": None,
            "missing_fields": [],
            "info_prompt": None
        }
        
        booking_updates = None
        if request.action_type in ['inquire', 'book_schedule', 'select_slot', 'provide_info', 'cancel_booking']:
            booking_updates = await booking_flow_manager.process_user_action(initial_state)
            initial_state.update(booking_updates)
            
            # Track booking flow
            await workflow_visualizer.track_node_execution(
                "booking_flow", 
                NodeStatus.COMPLETED,
                {"action_type": request.action_type, "user_info": request.user_info or {}},
                booking_updates or {}
            )

        # Skip main workflow for booking-specific steps; otherwise, run it
        if request.action_type in ['inquire', 'book_schedule', 'select_slot', 'provide_info', 'cancel_booking']:
            final_state = initial_state
        else:
            # Execute main LangGraph workflow with timeout protection
            try:
                import asyncio
                final_state = await asyncio.wait_for(
                    workflow.ainvoke(
                        initial_state,
                        config={
                            "recursion_limit": 10,
                            "max_search_iterations": 3,
                            "max_research_loops": 1
                        }
                    ),
                    timeout=settings.WORKFLOW_TIMEOUT  # Use configured timeout
                )
                
                # Skip unused nodes based on intent
                intent = final_state.get("intent", "general_info")
                await workflow_visualizer.skip_unused_nodes(intent)
                
            except asyncio.TimeoutError:
                logger.error("Workflow execution timed out after 120 seconds")
                final_state = {
                    **initial_state,
                    "response_message": "I apologize, but the request is taking longer than expected. Please try again with a simpler query or contact support if the issue persists.",
                    "suggested_actions": ["Try a simpler query", "Contact support", "Ask for help"],
                    "error": "workflow_timeout",
                    "workflow_complete": True
                }
            except Exception as workflow_error:
                logger.error(f"Workflow execution failed: {workflow_error}")
                final_state = {
                    **initial_state,
                    "response_message": "I encountered an error while processing your request. Please try again or contact support.",
                    "suggested_actions": ["Try again", "Contact support", "Ask for help"],
                    "error": str(workflow_error),
                    "workflow_complete": True
                }

        # Post booking actions
        if final_state.get("workflow_complete") and final_state.get("appointment_details"):
            try:
                appt = final_state["appointment_details"]
                summary = f"Property Tour - {appt.get('property_id', 'Property')}"
                description = f"Property visit scheduled by {appt.get('user_name')} (pets: {appt.get('user_pets', 'N/A')})"
                start_str = appt.get('slot') if isinstance(appt.get('slot'), str) else appt.get('slot', '')
                from datetime import datetime, timedelta
                start_dt = None
                end_dt = None
                if start_str:
                    # Expected format from booking flow: "YYYY-MM-DD HH:MM:SS"
                    try:
                        # Normalize potential "YYYY-MM-DD HH:MM:SS" to datetime
                        start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        # Fallback: try ISO parsing after replacing space with 'T'
                        try:
                            start_dt = datetime.fromisoformat(start_str.replace(' ', 'T').replace('Z', ''))
                        except Exception:
                            start_dt = None
                    if start_dt:
                        end_dt = start_dt + timedelta(hours=1)

                # Build comprehensive description with all user details
                detailed_description = f"""Property Tour Appointment

Client Information:
• Full Name: {appt.get('user_name', 'Not provided')}
• Email: {appt.get('user_email', 'Not provided')}
• Phone: {appt.get('user_phone', 'Not provided')}
• Pet Information: {appt.get('user_pets', 'Not specified')}

Property Details:
• Property ID: {appt.get('property_id', 'Not specified')}
• Tour Date: {start_dt.strftime('%A, %B %d, %Y at %I:%M %p') if start_dt else 'Not specified'}

Notes:
- Please arrive 5 minutes early
- Bring valid ID for verification
- Contact client at provided phone number if needed"""

                # Build Google Calendar event body with RFC3339 and explicit timeZone
                event_data = {
                    "summary": f"Property Tour - {appt.get('user_name', 'Client')}",
                    "description": detailed_description,
                    "start": {
                        "dateTime": (start_dt.isoformat() if start_dt else start_str.replace(' ', 'T')),
                        "timeZone": settings.GOOGLE_CALENDAR_TIMEZONE,
                    },
                    "end": {
                        "dateTime": (end_dt.isoformat() if end_dt else (start_str.replace(' ', 'T'))),
                        "timeZone": settings.GOOGLE_CALENDAR_TIMEZONE,
                    },
                    "attendees": [{"email": appt.get('user_email', '')}] if appt.get('user_email') else [],
                }
                cal_result = await calendar_tool.create_calendar_event(event_data)
                final_state["calendar_event_id"] = cal_result.get("event_id") if cal_result else None
                
                # Track calendar creation
                await workflow_visualizer.track_node_execution(
                    "create_calendar_event",
                    NodeStatus.COMPLETED,
                    event_data,
                    {"success": cal_result.get("success", False), "event_id": cal_result.get("event_id")}
                )
                
                phone = appt.get('user_phone')
                if phone:
                    appt_sms = {
                        **appt,
                        "formatted_date": (start_dt.strftime("%A, %B %d at %I:%M %p") if start_dt else (start_str or "")),
                        "id": cal_result.get("event_id") if cal_result else None,
                        "property_address": appt.get('property_id')
                    }
                    sms_result = await sms_tool.send_appointment_confirmation(phone, appt_sms)
                    final_state["sms_sent"] = sms_result.get("success")
                    final_state["sms_result"] = sms_result
                    
                    # Track SMS sending
                    await workflow_visualizer.track_node_execution(
                        "send_sms_confirmation",
                        NodeStatus.COMPLETED,
                        {"phone": phone, "appointment_data": appt_sms},
                        {"success": sms_result.get("success", False)}
                    )
            except Exception as e:
                logger.error(f"Post-booking actions failed: {e}")

        # Prefer booking flow values for interactive UX
        available_slots = final_state.get("available_slots") or (booking_updates.get("available_slots") if booking_updates else []) or []
        current_step = final_state.get("current_step") or (booking_updates.get("current_step") if booking_updates else None) or "property_search"
        requires_user_info = final_state.get("requires_user_info") if final_state.get("requires_user_info") is not None else ((booking_updates.get("requires_user_info") if booking_updates else False) or False)
        property_details = final_state.get("property_details") or (booking_updates.get("property_details") if booking_updates else None)
        suggested_actions = final_state.get("suggested_actions") or (booking_updates.get("suggested_actions") if booking_updates else []) or []
        response_message = final_state.get("response_message") or (booking_updates.get("response_message") if booking_updates else None) or "I'm here to help!"
        next_field = final_state.get("next_field") or (booking_updates.get("next_field") if booking_updates else None)
        missing_fields = final_state.get("missing_fields") or (booking_updates.get("missing_fields") if booking_updates else []) or []
        info_prompt = final_state.get("info_prompt") or (booking_updates.get("info_prompt") if booking_updates else None)

        # Complete workflow tracking
        await workflow_visualizer.complete_execution({
            "response": response_message,
            "properties_count": len(final_state.get("properties", [])),
            "workflow_complete": final_state.get("workflow_complete", False)
        })

        # Persist minimal chat history for non-UI commands
        if request.user_id and request.action_type not in ['inquire', 'book_schedule', 'select_slot', 'provide_info', 'cancel_booking']:
            chat_history.append_message(request.user_id, "user", request.query)
            chat_history.append_message(request.user_id, "assistant", response_message)

        # Persist updated filters from final state
        try:
            if request.user_id:
                search_session.set_filters(request.user_id, final_state.get("search_filters") or {})
        except Exception:
            pass

        return ChatResponse(
            response=response_message,
            intent=final_state.get("intent"),
            entities={},
            suggested_actions=suggested_actions,
            properties=final_state.get("properties", []),
            available_slots=available_slots,
            current_step=current_step,
            requires_user_info=requires_user_info,
            property_details=property_details,
            appointment_details=final_state.get("appointment_details"),
            next_field=next_field,
            missing_fields=missing_fields,
            info_prompt=info_prompt
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {
        "message": "PropertyTek AI Chatbot API",
        "version": "2.0.0",
        "powered_by": "LangGraph",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }