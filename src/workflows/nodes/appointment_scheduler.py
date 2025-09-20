"""
Appointment Scheduler Node - Gets available appointment slots
"""

import logging
from .base import BaseNode, error_handler
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)


class AppointmentSchedulerNode(BaseNode):
    """Node for getting available appointment slots"""
    
    @error_handler
    async def get_available_slots(self, state: WorkflowState, config=None) -> dict:
        """Get available slots - LangGraph optimized"""
        duration = getattr(config, "slot_duration_minutes", None) if config else None
        duration = duration or 60
        slots = await self.calendar_tool.get_fixed_slots_next_day(duration_minutes=duration)
        updates = {"available_slots": slots}
        
        logger.info(f"Found {len(slots)} available slots")
        if slots:
            logger.info(f"First slot: {slots[0]}")
        
        # LangGraph pattern: Conditional fallback
        if not slots:
            updates["fallback_context"] = self._create_fallback_context("no_appointments", {
                "requested_timeframe": "next 3 days",
                "user_query": state["user_query"]
            })
        
        return updates