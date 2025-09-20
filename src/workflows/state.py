"""
Workflow State Management for LangGraph
"""

from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict


class WorkflowState(TypedDict):
    """Main workflow state for property management chatbot"""
    
    # User input and context
    user_query: str
    user_id: Optional[str]
    conversation_history: Optional[str]
    messages: List[Dict[str, Any]]
    
    # Intent and entities
    intent: Optional[str]
    entities: Dict[str, Any]
    confidence: Optional[str]
    
    # Property search results
    properties: List[Dict[str, Any]]
    search_filters: Dict[str, Any]
    search_query: Optional[str]
    queries: List[str]
    reflection_notes: Optional[str]
    needs_more_research: Optional[bool]
    fallback_context: Optional[Dict[str, Any]]
    
    # Appointment scheduling
    available_slots: List[Dict[str, Any]]
    selected_slot: Optional[Dict[str, Any]]
    appointment_details: Optional[Dict[str, Any]]
    
    # User information for booking
    user_name: Optional[str]
    user_email: Optional[str]
    user_phone: Optional[str]
    user_pets: Optional[str]
    
    # Calendar and SMS results
    calendar_event_id: Optional[str]
    sms_sent: Optional[bool]
    sms_result: Optional[Dict[str, Any]]
    
    # Response generation
    response_message: str
    suggested_actions: List[str]
    
    # Error handling
    error: Optional[str]
    
    # Workflow control
    next_step: Optional[str]
    workflow_complete: bool
    
    # Loop prevention counters
    reflection_loops: Optional[int]
    search_iterations: Optional[int]