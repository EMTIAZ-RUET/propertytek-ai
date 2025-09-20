"""
Intent Analyzer Node - Analyzes user intent and extracts entities
"""

import logging
from .base import BaseNode, error_handler, track_workflow_execution
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)


class IntentAnalyzerNode(BaseNode):
    """Node for analyzing user intent and extracting entities"""
    
    @error_handler
    @track_workflow_execution("analyze_intent")
    async def analyze_intent(self, state: WorkflowState, config=None) -> dict:
        """Simplified intent analysis for LangGraph workflow"""
        user_query = state["user_query"]
        # Lightweight heuristic to bias toward property search when user specifies filters like bedrooms
        heuristic_intent = None
        try:
            q = user_query.lower().strip()
            bedroom_keywords = ["bed", "beds", "bedroom", "br", "studio"]
            housing_keywords = ["apartment", "house", "condo", "rental", "rent", "lease", "property"]
            non_property_keywords = [
                "tshirt", "t-shirt", "shirt", "jeans", "clothes", "dress", "shoes", "sneakers",
                "cosmetics", "makeup", "lipstick", "foundation", "eyeliner", "mascara",
                "phone", "iphone", "android", "laptop", "macbook", "headphones", "earbuds", "charger",
                "grocery", "groceries", "fruits", "vegetables", "milk",
                "perfume", "shampoo", "soap", "toothpaste", "toys", "gaming",
                "electronics", "watch", "camera", "television", "tv"
            ]
            greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you", "how are you doing", "what's up", "whats up", "howdy"]
            # Self-introduction patterns like "I am Emtiaz", "I'm John", "this is Sarah"
            self_intro_keywords = ["i am ", "i'm ", "im ", "this is ", "my name is "]
            booking_keywords = ["book", "booking", "schedule", "viewing", "tour", "available dates", "available date", "schedule viewing", "schedule a tour", "check dates"]
            numeric = any(char.isdigit() for char in q)
            # Detect explicit self-introductions without adding canned "I'm doing well" replies
            if any(k in q for k in self_intro_keywords) and len(q) <= 60:
                heuristic_intent = "self_introduction"
            # Greetings take priority to enable friendly small talk (only when actually greeted)
            if heuristic_intent is None and any(k in q for k in greeting_keywords) and len(q) <= 60:
                heuristic_intent = "greeting"
            # Strong property indicators
            if any(k in q for k in bedroom_keywords) or any(k in q for k in housing_keywords):
                heuristic_intent = "property_search"
            # Booking/viewing indicators
            if any(k in q for k in booking_keywords):
                # If user mentions booking without property context, still keep as property_search for now
                # Main workflow routes schedule_tour explicitly when downstream detects action_type
                heuristic_intent = heuristic_intent or "property_search"
            # If explicit non-property product keywords present and no strong property indicators, mark non_property
            elif any(k in q for k in non_property_keywords):
                heuristic_intent = "non_property"
            # Short numeric like "2 beds" should be treated as property_search
            if numeric and any(k in q for k in bedroom_keywords):
                heuristic_intent = "property_search"
        except Exception:
            pass

        result = await self.openai_service.analyze_intent(user_query)
        
        intent_value = heuristic_intent or result.get("intent", "ask_question")
        logger.info(f"Intent: {intent_value} for query: {state['user_query']}")
        
        # If the user asked about non-property/ecommerce topics, extract criteria only and do not search
        if intent_value == "non_property":
            criteria = await self.property_service.extract_search_criteria(user_query)
            return {"intent": intent_value, "search_filters": criteria, "properties": []}
        
        return {"intent": intent_value}