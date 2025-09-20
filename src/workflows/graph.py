"""
LangGraph Workflow Definition
"""

from langgraph.graph import StateGraph, END
from src.workflows.state import WorkflowState
from src.workflows.workflow_nodes import WorkflowNodes
from src.workflows.configuration import Configuration


def create_property_workflow() -> StateGraph:
    """Create the main property management workflow graph"""
    
    # Initialize nodes
    nodes = WorkflowNodes()
    
    # Create the graph with configuration schema
    workflow = StateGraph(WorkflowState, config_schema=Configuration)
    
    # Add nodes
    workflow.add_node("analyze_intent", nodes.analyze_intent)
    workflow.add_node("search_properties", nodes.search_properties)
    workflow.add_node("reflect", nodes.reflect)
    workflow.add_node("get_available_slots", nodes.get_available_slots)
    workflow.add_node("collect_user_info", nodes.collect_user_info)
    workflow.add_node("create_calendar_event", nodes.create_calendar_event)
    workflow.add_node("send_sms_confirmation", nodes.send_sms_confirmation)
    workflow.add_node("generate_response", nodes.generate_response)
    
    # Set entry point - start with intent analysis to route properly
    workflow.set_entry_point("analyze_intent")
    
    # Define routing functions using LangGraph's conditional routing
    def route_from_intent(state: WorkflowState) -> str:
        """Route from analyze_intent based on intent type"""
        intent = state.get("intent", "general_info")
        
        # Intent-based routing map
        intent_routes = {
            "property_search": "search_properties",
            "schedule_tour": "get_available_slots", 
            "confirm_booking": "create_calendar_event",
            # For non-property/ecommerce queries, skip searching and go straight to response
            "non_property": "generate_response"
        }
        
        return intent_routes.get(intent, "generate_response")
    
    def route_next_step(state: WorkflowState) -> str:
        """Route to next step based on workflow state"""
        next_step = state.get("next_step", "generate_response")
        
        # Valid routing options - LangGraph will handle invalid routes
        valid_routes = {
            "search_properties", "get_available_slots", "collect_user_info",
            "create_calendar_event", "send_sms_confirmation", "generate_response"
        }
        
        return next_step if next_step in valid_routes else "generate_response"
    
    def route_after_search(state: WorkflowState) -> str:
        """Route after property search - always go to response generation"""
        # Check if we have a fallback context indicating no criteria
        fallback_context = state.get("fallback_context", {})
        if fallback_context.get("type") == "need_criteria":
            return "generate_response"
        
        # Check if we've exceeded max search iterations to prevent infinite loops
        search_count = state.get("search_iterations", 0)
        max_iterations = state.get("max_search_iterations", 3)
        
        if search_count >= max_iterations:
            return "generate_response"
        
        # Check if we have properties or need to reflect
        properties = state.get("properties", [])
        if properties:
            return "generate_response"
        
        # Only go to reflect if we haven't exceeded max iterations
        return "reflect"
    
    def route_after_slots(state: WorkflowState) -> str:
        """Route after getting available slots"""
        # Always go to user info collection after showing slots
        return "collect_user_info"
    
    def route_after_user_info(state: WorkflowState) -> str:
        """Route after collecting user info"""
        # Check if we have all required info for booking
        required_fields = ["user_name", "user_email", "user_phone", "user_pets"]
        if all(state.get(field) for field in required_fields):
            return "create_calendar_event"
        return "generate_response"
    
    def route_after_calendar(state: WorkflowState) -> str:
        """Route after creating calendar event"""
        # If event created successfully, send SMS
        if state.get("calendar_event_id"):
            return "send_sms_confirmation"
        return "generate_response"
    
    # Add conditional edges using specific routing functions
    workflow.add_conditional_edges(
        "analyze_intent",
        route_from_intent,
        {
            "search_properties": "search_properties",
            "get_available_slots": "get_available_slots",
            "create_calendar_event": "create_calendar_event",
            "generate_response": "generate_response"
        }
    )
    
    # After property search, route conditionally
    workflow.add_conditional_edges(
        "search_properties",
        route_after_search,
        {
            "reflect": "reflect",
            "generate_response": "generate_response"
        }
    )
    
    # Reflection routing: either loop to search or finalize
    def route_after_reflect(state: WorkflowState) -> str:
        """Route after reflection - prevent infinite loops"""
        # Check if we've exceeded max research loops
        reflection_count = state.get("reflection_loops", 0)
        max_loops = state.get("max_research_loops", 1)
        
        if reflection_count >= max_loops:
            return "generate_response"
        
        next_step = state.get("next_step", "generate_response")
        return next_step if next_step in {"search_properties", "generate_response"} else "generate_response"

    workflow.add_conditional_edges(
        "reflect",
        route_after_reflect,
        {
            "search_properties": "search_properties",
            "generate_response": "generate_response"
        }
    )

    # Available slots routing based on user info
    workflow.add_conditional_edges(
        "get_available_slots",
        route_after_slots,
        {
            "collect_user_info": "collect_user_info",
            "generate_response": "generate_response"
        }
    )
    
    # User info collection routing
    workflow.add_conditional_edges(
        "collect_user_info",
        route_after_user_info,
        {
            "create_calendar_event": "create_calendar_event",
            "generate_response": "generate_response"
        }
    )
    
    # Calendar event routing
    workflow.add_conditional_edges(
        "create_calendar_event",
        route_after_calendar,
        {
            "send_sms_confirmation": "send_sms_confirmation",
            "generate_response": "generate_response"
        }
    )
    
    # SMS confirmation always goes to response
    workflow.add_conditional_edges(
        "send_sms_confirmation",
        lambda state: "generate_response",
        {"generate_response": "generate_response"}
    )
    
    # Add edge from generate_response to END
    workflow.add_edge("generate_response", END)
    
    # Compile with recursion limit configuration
    compiled_workflow = workflow.compile()
    
    # Set default configuration to prevent infinite loops
    compiled_workflow.config = {
        "recursion_limit": 10,
        "max_search_iterations": 3,
        "max_research_loops": 1
    }
    
    return compiled_workflow

# -----------------------------------------------------------------------------
# Workflow Graph Visualization (for quick reference)
#
# Nodes (with roles):
# - analyze_intent           : Entry / router (decides next step based on intent)
# - search_properties        : Property search (may lead to reflect or directly to response)
# - reflect                  : Decision node to refine search or finalize
# - get_available_slots      : Retrieves appointment slots (booking flow)
# - collect_user_info        : Gathers user details required for booking
# - create_calendar_event    : Creates Google Calendar event
# - send_sms_confirmation    : Sends SMS confirmation for booking
# - generate_response        : Final response aggregator (then END)
#
# Edges (routing conditions):
# - analyze_intent -> search_properties      [intent == "property_search"]
# - analyze_intent -> get_available_slots    [intent == "schedule_tour"]
# - analyze_intent -> create_calendar_event  [intent == "confirm_booking"]
# - analyze_intent -> generate_response      [else or intent == "non_property"]
#
# - search_properties -> reflect             [no results and within limits]
# - search_properties -> generate_response   [have results OR exceeded limits OR need_criteria]
#
# - reflect -> search_properties             [next_step == "search_properties" AND loop limit not exceeded]
# - reflect -> generate_response             [else]
#
# - get_available_slots -> collect_user_info [always]
# - collect_user_info -> create_calendar_event [have user_name, user_email, user_phone, user_pets]
# - collect_user_info -> generate_response   [missing required info]
#
# - create_calendar_event -> send_sms_confirmation [calendar_event_id set]
# - create_calendar_event -> generate_response     [else]
# - send_sms_confirmation -> generate_response     [always]
# - generate_response -> END
#
# ASCII map (monospace view):
#
#                    +------------------+
#                    |  analyze_intent  |
#                    +---------+--------+
#                              | (property_search)
#                              v
#                    +----------------------+
#   (default/non_)   |   search_properties  |----+  (no results, under limits)
#   property  +----->+----------------------+    |
#     |                |                      (results/limits/need_criteria)
#     | (else)         v                           |
#     |            +---------+                     v
#     +----------->| reflect |----------------> generate_response --> END
#                  +----+----+  (next_step==search_properties)
#                       |
#                       v
#                search_properties (loop)
#
#    (schedule_tour)
# analyze_intent ---------------> get_available_slots --> collect_user_info --+--> create_calendar_event --> send_sms_confirmation --+
#                                                                             |                                         |           |
#                                                                             | (missing info)                          |           v
#                                                                             +--------------> generate_response <------+-----------+
#                                                                                                           |
#                                                                                                           +--> END
# -----------------------------------------------------------------------------