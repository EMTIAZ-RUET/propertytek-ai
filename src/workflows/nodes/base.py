"""
Base Node Class with Common LangGraph Patterns
"""

import logging
from typing import Dict, Any, Callable
from functools import wraps
import asyncio

from src.workflows.state import WorkflowState
from src.services.property_service import PropertyService
from src.tools.calendar_tool import CalendarTool
from src.tools.sms_tool import SMSTool
from src.services.openai_service import OpenAIService
from src.visualization.workflow_visualizer import workflow_visualizer, NodeStatus

logger = logging.getLogger(__name__)


def error_handler(func: Callable) -> Callable:
    """LangGraph decorator for automatic error handling returning deltas"""
    @wraps(func)
    async def wrapper(self, state: WorkflowState, config=None) -> Dict[str, Any]:
        try:
            return await func(self, state, config)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return {"error": str(e)}
    return wrapper


def track_workflow_execution(node_name: str):
    """Decorator to automatically track workflow execution in the visualizer"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, state: WorkflowState, config=None) -> Dict[str, Any]:
            # Track node start
            await workflow_visualizer.track_node_execution(
                node_name, 
                NodeStatus.RUNNING,
                {"user_query": state.get("user_query", ""), "user_id": state.get("user_id", "")}
            )
            
            try:
                # Execute the node
                result = await func(self, state, config)
                
                # Track successful completion
                await workflow_visualizer.track_node_execution(
                    node_name, 
                    NodeStatus.COMPLETED,
                    output_data=result
                )
                
                return result
                
            except Exception as e:
                # Track error
                await workflow_visualizer.track_node_execution(
                    node_name, 
                    NodeStatus.ERROR,
                    error_message=str(e)
                )
                raise e
                
        return wrapper
    return decorator


class BaseNode:
    """Base class for all LangGraph workflow nodes"""
    
    def __init__(self):
        self.property_service = PropertyService()
        self.calendar_tool = CalendarTool()
        self.sms_tool = SMSTool()
        self.openai_service = OpenAIService()
        
        # Common field mappings
        self.user_info_fields = {
            "user_name": ["user_name", "name"],
            "user_email": ["user_email", "email"], 
            "user_phone": ["user_name", "phone"],
            "user_pets": ["pets", "pet_policy"]
        }
    
    def _create_fallback_context(self, fallback_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph pattern: Standardized fallback context creation"""
        return {"type": fallback_type, "details": details}
    
    def _extract_field_value(self, entities: Dict[str, Any], field_keys: list, state: WorkflowState) -> str:
        """LangGraph pattern: Smart field extraction with fallback"""
        # Try entities first
        for key in field_keys:
            if entities.get(key):
                return entities[key]
        
        # Fallback to history extraction
        return self._extract_from_history(field_keys[0], state)
    
    def _extract_from_history(self, field: str, state: WorkflowState) -> str:
        """LangGraph pattern: History extraction with mapping"""
        history = state.get("conversation_history", "").lower()
        
        # LangGraph pattern: Field extraction mapping
        extraction_patterns = {
            "name": {"emtiaz": "Emtiaz", "riad": "Riad"},
            "user_name": {"emtiaz": "Emtiaz", "riad": "Riad"}
        }
        
        patterns = extraction_patterns.get(field, {})
        for pattern, value in patterns.items():
            if pattern in history:
                return value
                
        return None