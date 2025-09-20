"""
SMS Sender Node - Sends SMS confirmations for appointments
"""

import logging
from .base import BaseNode, error_handler
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)


class SMSSenderNode(BaseNode):
    """Node for sending SMS confirmations for appointments"""
    
    @error_handler
    async def send_sms_confirmation(self, state: WorkflowState, config=None) -> dict:
        """Send SMS - LangGraph optimized"""
        # LangGraph pattern: Conditional execution
        if not (state.get("user_phone") and state.get("appointment_details")):
            logger.info("Skipping SMS - missing phone or appointment details")
            return {}
        if config and getattr(config, "enable_sms", True) is False:
            logger.info("Skipping SMS - disabled by configuration")
            return {}
            
        sms_result = await self.sms_tool.send_appointment_confirmation(
            phone_number=state["user_phone"],
            appointment_details=state["appointment_details"]
        )
        
        # LangGraph pattern: Bulk state update
        updates = {
            "sms_sent": sms_result.get("success", False),
            "sms_result": sms_result
        }
        
        logger.info(f"SMS sent: {updates['sms_sent']}")
        return updates