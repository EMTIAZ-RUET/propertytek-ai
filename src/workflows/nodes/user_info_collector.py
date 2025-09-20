"""
User Info Collector Node - Collects user information for booking
"""

import logging
import re
from .base import BaseNode, error_handler
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)


class UserInfoCollectorNode(BaseNode):
    """Node for collecting user information for booking"""
    
    @error_handler
    async def collect_user_info(self, state: WorkflowState, config=None) -> dict:
        """Interactive user info collection with validation"""
        
        user_query = state.get("user_query", "").lower()
        current_step = state.get("current_step", "")
        user_info = state.get("user_info", {})
        
        # If user provided info in the query, extract it
        if state.get("action_type") == "provide_info" or "my name is" in user_query or "email" in user_query or "phone" in user_query:
            extracted_info = self._extract_user_info(user_query, user_info)
            user_info.update(extracted_info)
        
        # Check required fields
        required_fields = ["name", "email", "phone"]
        missing_fields = [field for field in required_fields if not user_info.get(field)]
        
        updates = {
            "user_info": user_info,
            "user_name": user_info.get("name"),
            "user_email": user_info.get("email"), 
            "user_phone": user_info.get("phone"),
            "user_pets": user_info.get("pets")
        }
        
        if missing_fields:
            # Still missing info - ask for it
            updates.update({
                "current_step": "info_collection",
                "requires_user_info": True,
                "missing_fields": missing_fields,
                "next_step": "generate_response"
            })
            logger.info(f"Still missing user info: {missing_fields}")
        else:
            # All info collected - proceed to booking
            updates.update({
                "current_step": "booking_confirmation",
                "requires_user_info": False,
                "next_step": "create_calendar_event"
            })
            logger.info("All user info collected, proceeding to booking")
        
        return updates
    
    def _extract_user_info(self, user_query: str, existing_info: dict) -> dict:
        """Extract user information from natural language input"""
        extracted = {}
        
        # Extract name
        name_patterns = [
            r"my name is ([a-zA-Z\s]+)",
            r"i'm ([a-zA-Z\s]+)",
            r"i am ([a-zA-Z\s]+)",
            r"name:\s*([a-zA-Z\s]+)",
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                extracted["name"] = match.group(1).strip().title()
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, user_query)
        if email_match:
            extracted["email"] = email_match.group(0).lower()
        
        # Extract phone
        phone_patterns = [
            r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',
            r'(\d{10})',
            r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, user_query)
            if match:
                # Clean up phone number
                phone = re.sub(r'[^\d+]', '', match.group(1))
                if len(phone) == 10:
                    phone = f"+1{phone}"
                elif len(phone) == 11 and phone.startswith('1'):
                    phone = f"+{phone}"
                extracted["phone"] = phone
                break
        
        # Extract pets info
        pets_patterns = [
            r"i have (no pets|no pet|cats?|dogs?|cats? and dogs?)",
            r"pets?:\s*(no|none|cats?|dogs?|cats? and dogs?)",
            r"(no pets|cats?|dogs?|cats? and dogs?)"
        ]
        
        for pattern in pets_patterns:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                pets_text = match.group(1).lower()
                if "no" in pets_text or "none" in pets_text:
                    extracted["pets"] = "No Pets"
                elif "cat" in pets_text and "dog" in pets_text:
                    extracted["pets"] = "Cats and Dogs"
                elif "cat" in pets_text:
                    extracted["pets"] = "Cats"
                elif "dog" in pets_text:
                    extracted["pets"] = "Dogs"
                break
        
        logger.info(f"Extracted user info: {extracted}")
        return extracted