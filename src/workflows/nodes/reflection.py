"""
Reflection/Evaluation Node - decides whether to loop back to search
"""

import logging
from typing import Dict, Any
from .base import BaseNode, error_handler, track_workflow_execution
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)


class ReflectionNode(BaseNode):
    """Evaluates current results and decides next step"""

    @error_handler
    @track_workflow_execution("reflect")
    async def reflect(self, state: WorkflowState, config=None) -> Dict[str, Any]:
        """Return deltas: notes, needs_more_research, next_step"""
        properties = state.get("properties", [])
        user_query = state.get("user_query", "")
        fallback_context = state.get("fallback_context", {})

        # Check if we have a fallback context indicating no meaningful criteria
        if fallback_context.get("type") == "need_criteria":
            logger.info("No meaningful search criteria provided. Ending search loop.")
            return {
                "reflection_notes": "User needs to provide more specific search criteria.",
                "needs_more_research": False,
                "next_step": "generate_response"
            }

        # Simple heuristic: if no properties, or vague intent, request another search
        needs_more = len(properties) == 0

        loops_allowed = getattr(config, "max_research_loops", 1) if config else 1
        current_loops = int(state.get("reflection_loops", 0) or 0)

        if needs_more and current_loops < loops_allowed:
            notes = "Insufficient results. Try refining search."
            return {
                "reflection_notes": notes,
                "needs_more_research": True,
                "reflection_loops": current_loops + 1,
                "next_step": "search_properties"
            }

        # Otherwise, proceed to finalize
        notes = "Results sufficient or loop budget exhausted. Proceed to finalize."
        return {
            "reflection_notes": notes,
            "needs_more_research": False,
            "next_step": "generate_response"
        }


