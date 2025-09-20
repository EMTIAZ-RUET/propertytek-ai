"""
Calendar Manager Node - Creates calendar events for appointments
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from .base import BaseNode, error_handler
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)


class CalendarManagerNode(BaseNode):
    """Node for creating calendar events for appointments"""
    
    @error_handler
    async def create_calendar_event(self, state: WorkflowState, config=None) -> dict:
        """Create calendar event - LangGraph optimized"""
        appointment_time = datetime.now() + timedelta(days=1, hours=11)
        property_address = self._get_property_address(state)
        
        # LangGraph pattern: Template-based event creation
        calendar_event = self._build_calendar_event(state, appointment_time, property_address)
        result = await self.calendar_tool.create_calendar_event(calendar_event)
        
        # LangGraph pattern: Conditional state update
        if result.get("success"):
            updates = {
                "calendar_event_id": result.get("event_id"),
                "appointment_details": {
                    "property_address": property_address,
                    "formatted_date": appointment_time.strftime("%A, %B %d at %I:%M %p"),
                    "id": result.get("event_id")
                }
            }
        else:
            updates = {"error": result.get("error", "Failed to create calendar event")}
        
        logger.info(f"Calendar event created: {result.get('success', False)}")
        return updates
    
    def _get_property_address(self, state: WorkflowState) -> str:
        """LangGraph pattern: Safe property address extraction"""
        properties = state.get("properties", [])
        return properties[0].get("address", "Property Tour Location") if properties else "Property Tour Location"
    
    def _build_calendar_event(self, state: WorkflowState, appointment_time: datetime, property_address: str) -> Dict[str, Any]:
        """LangGraph pattern: Template-based calendar event building"""
        return {
            'summary': f'Property Tour - {property_address}',
            'description': f"""
Property Tour Appointment

Client Details:
- Name: {state.get('user_name', 'N/A')}
- Email: {state.get('user_email', 'N/A')}
- Phone: {state.get('user_phone', 'N/A')}
- Pets: {state.get('user_pets', 'N/A')}

Property: {property_address}
            """.strip(),
            'start': {
                'dateTime': appointment_time.isoformat(),
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': (appointment_time + timedelta(hours=1)).isoformat(),
                'timeZone': 'America/Chicago',
            },
            'attendees': [{'email': state.get('user_email', '')}] if state.get('user_email') else [],
        }