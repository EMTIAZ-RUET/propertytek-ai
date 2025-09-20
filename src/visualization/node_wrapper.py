"""
LangGraph Node Wrapper for Real-time Visualization Tracking
"""

import asyncio
import functools
from typing import Dict, Any, Callable
from src.visualization.workflow_visualizer import workflow_visualizer, NodeStatus

def track_node_execution(node_id: str):
    """Decorator to track LangGraph node execution in real-time with live data flow"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, state: Dict[str, Any], config=None):
            # Track node start with detailed input data
            input_data = {
                "user_query": state.get("user_query", ""),
                "intent": state.get("intent", ""),
                "properties_count": len(state.get("properties", [])),
                "current_step": state.get("current_step", ""),
                "user_info": {k: v for k, v in state.items() if k.startswith("user_") and k != "user_query"},
                "reflection_loops": state.get("reflection_loops", 0),
                "available_slots_count": len(state.get("available_slots", [])),
                "workflow_complete": state.get("workflow_complete", False),
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Start tracking with live updates
            await workflow_visualizer.track_node_execution(
                node_id, 
                NodeStatus.RUNNING, 
                input_data
            )
            
            try:
                # Execute the actual node function
                result = await func(self, state, config)
                
                # Track successful completion with comprehensive output data
                output_data = {}
                if isinstance(result, dict):
                    output_data = {
                        "intent": result.get("intent", ""),
                        "confidence": result.get("confidence", 0),
                        "properties_found": len(result.get("properties", [])),
                        "response_message": result.get("response_message", "")[:200] if result.get("response_message") else "",
                        "next_step": result.get("next_step", ""),
                        "workflow_complete": result.get("workflow_complete", False),
                        "available_slots": len(result.get("available_slots", [])),
                        "calendar_event_id": result.get("calendar_event_id", ""),
                        "sms_sent": result.get("sms_sent", False),
                        "reflection_notes": result.get("reflection_notes", "")[:100] if result.get("reflection_notes") else "",
                        "needs_more_research": result.get("needs_more_research", False),
                        "entities": result.get("entities", {}),
                        "search_filters": result.get("search_filters", {}),
                        "execution_time": asyncio.get_event_loop().time() - input_data["timestamp"]
                    }
                
                await workflow_visualizer.track_node_execution(
                    node_id,
                    NodeStatus.COMPLETED,
                    input_data,
                    output_data
                )
                
                return result
                
            except Exception as e:
                # Track error with detailed error information
                await workflow_visualizer.track_node_execution(
                    node_id,
                    NodeStatus.ERROR,
                    input_data,
                    {"error_type": type(e).__name__, "error_details": str(e)[:200]},
                    str(e)
                )
                raise
                
        return wrapper
    return decorator
