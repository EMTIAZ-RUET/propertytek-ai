"""
Response Generator Node - Generates final responses to users
"""

import logging
from typing import Dict, Any
from .base import BaseNode, error_handler, track_workflow_execution
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)


class ResponseGeneratorNode(BaseNode):
    """Node for generating final responses to users"""
    
    @track_workflow_execution("generate_response")
    async def generate_response(self, state: WorkflowState, config=None) -> dict:
        """Generate response - LangGraph optimized with error recovery"""
        try:
            # LangGraph pattern: Parameter extraction
            response_params = self._extract_response_params(state)
            response = await self.openai_service.generate_response(**response_params)
            
            # LangGraph pattern: Response processing
            updates = self._process_response(response)
            
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            # LangGraph pattern: Error recovery with fallback
            updates = await self._handle_response_error(state, e)
        
        updates["workflow_complete"] = True
        logger.info("Response generated successfully")
        return updates
    
    def _extract_response_params(self, state: WorkflowState) -> Dict[str, Any]:
        """LangGraph pattern: Parameter extraction for response generation"""
        return {
            "user_query": state.get("user_query", ""),
            "intent": state.get("intent", "property_search"),
            "properties": state.get("properties", []),
            "available_slots": state.get("available_slots", []),
            "appointment_details": state.get("appointment_details"),
            "error": state.get("error"),
            "fallback_context": state.get("fallback_context"),
            "messages": state.get("messages", []),
            "search_filters": state.get("search_filters")
        }
    
    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph pattern: Response processing and return updates"""
        updates: Dict[str, Any] = {}
        updates["response_message"] = response.get("message", "I'm here to help you with your property needs.")
        actions = response.get("suggested_actions", [])
        updates["suggested_actions"] = [str(action) for action in actions[:3]] if actions else ["Ask about properties", "Schedule a tour", "Get help"]
        return updates
    
    async def _handle_response_error(self, state: WorkflowState, error: Exception) -> Dict[str, Any]:
        """LangGraph pattern: Error recovery with dynamic fallback"""
        try:
            error_response = await self.openai_service.generate_response(
                user_query=state["user_query"],
                intent=state.get("intent", "unknown"),
                fallback_context=self._create_fallback_context("general_failure", {
                    "error_type": "system_error",
                    "user_query": state["user_query"],
                    "available_services": ["property search", "tour scheduling", "general questions"]
                })
            )
            return self._process_response(error_response)
        except:
            # LangGraph pattern: Ultimate fallback
            return {
                "response_message": "I apologize, but I encountered an error. Please try again.",
                "suggested_actions": ["Try rephrasing your question", "Contact support", "Ask for help"]
            }