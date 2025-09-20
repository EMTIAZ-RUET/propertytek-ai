"""
LangGraph Property Search Node - Simplified property search
"""

import logging
from typing import Dict, Any, Optional
from .base import BaseNode, error_handler, track_workflow_execution
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)


class PropertySearchNode(BaseNode):
    """LangGraph node for property search"""
    
    @error_handler
    @track_workflow_execution("search_properties")
    async def search_properties(self, state: WorkflowState, config=None) -> dict:
        """Property search with criteria extraction"""
        
        user_query = state.get("user_query", "")
        logger.info(f"Searching properties for query: {user_query}")
        
        # Extract search criteria for this turn
        extracted = await self.property_service.extract_search_criteria(user_query)

        # Merge with prior criteria across turns
        prior: Dict[str, Any] = state.get("search_filters") or {}
        criteria: Dict[str, Any] = {**prior}
        for k, v in (extracted or {}).items():
            if v not in (None, "", [], {}):
                criteria[k] = v

        # If this turn contains no property hints and extraction found nothing, avoid using stale filters
        def _has_property_hints(text: str) -> bool:
            t = (text or "").lower().strip()
            if not t:
                return False
            bedroom_keywords = ["bed", "beds", "bedroom", "br", "studio"]
            housing_keywords = ["apartment", "house", "condo", "rental", "rent", "lease", "property"]
            has_keywords = any(k in t for k in bedroom_keywords + housing_keywords)
            import re
            has_bed_num = bool(re.search(r"\b(\d+)\s*(bed|beds|bedroom|bedrooms|br)\b", t))
            return has_keywords or has_bed_num

        non_null_extracted = [k for k, v in (extracted or {}).items() if v not in (None, "", [], {})]
        if not non_null_extracted and not _has_property_hints(user_query):
            # Reset filters for this turn and ask for criteria instead of returning default results
            state.update({
                "properties": [],
                "search_filters": {},
                "fallback_context": {
                    "type": "need_criteria",
                    "details": {
                        "missing": ["location", "budget", "bedrooms", "pets", "available date"],
                        "clarify_prompt": self._get_clarification_prompt(user_query)
                    }
                }
            })
            return state

        # Guardrail: non-property heuristic (quick keyword screen)
        if self._looks_non_property(user_query) and not any(
            criteria.get(k) for k in ["address", "bedrooms", "rent_min", "rent_max", "rent_exact", "pets", "available_date"]
        ):
            state.update({
                "properties": [],
                "search_filters": criteria,
                "fallback_context": {
                    "type": "general_failure",
                    "details": {
                        "reason": "non_property",
                        "message": "I can help with Texas home rentals: city, budget, bedrooms, pets, move-in date."
                    }
                }
            })
            return state

        # Enforce Texas-only cities with friendly redirect
        original_location_input = (extracted or {}).get("address") or ""
        criteria, texas_redirect = self._enforce_texas_only(criteria)
        if texas_redirect:
            state.update({
                "properties": [],
                "search_filters": criteria,
                "fallback_context": {
                    "type": "no_properties",
                    "details": {
                        "query": user_query,
                        "filters": criteria,
                        "suggested_areas": ["Houston", "Dallas", "Austin", "San Antonio"],
                        "original_location": original_location_input
                    }
                }
            })
            return state
        
        # Counter-question strategy: prioritize missing info in strict order
        missing_order = ["address", "bedrooms", "rent_min/rent_max/rent_exact", "pets"]
        def _has_budget(c: Dict[str, Any]) -> bool:
            return any(c.get(k) not in (None, "", [], {}) for k in ["rent_min", "rent_max", "rent_exact"])
        missing_fields = []
        if not criteria.get("address"):
            missing_fields.append("location")
        if not criteria.get("bedrooms"):
            missing_fields.append("bedrooms")
        if not _has_budget(criteria):
            missing_fields.append("budget")
        # Ask about pets only if pets were mentioned or we already have other strong filters
        ql = (user_query or "").lower()
        pets_hint = ("pet" in ql) or bool(criteria.get("address") or criteria.get("bedrooms") or _has_budget(criteria))
        if not criteria.get("pets") and pets_hint:
            missing_fields.append("pets")

        # If we have no meaningful criteria at all, ask for the highest-priority one
        meaningful_fields = [k for k, v in (criteria or {}).items() if v not in (None, "", [], {})]
        if not meaningful_fields:
            prompt_by_priority = None
            if not criteria.get("address"):
                prompt_by_priority = "Which city or area are you looking for? I have properties in Austin, Dallas, Houston, San Antonio, and Fort Worth."
            elif not criteria.get("bedrooms"):
                prompt_by_priority = "How many bedrooms do you need?"
            elif not _has_budget(criteria):
                prompt_by_priority = "What's your monthly budget range?"
            elif not criteria.get("pets") and pets_hint:
                prompt_by_priority = "Do you have any pets I should know about?"

            state.update({
                "properties": [],
                "search_filters": criteria,
                "fallback_context": {
                    "type": "need_criteria",
                    "details": {
                        "missing": ["location", "budget", "bedrooms", "pets", "available date"],
                        "clarify_prompt": prompt_by_priority or self._get_clarification_prompt(user_query)
                    }
                }
            })
            return state
        
        # Search with merged criteria
        properties = self.property_service.search_with_criteria(criteria)
        
        # Update state with results
        formatted_props = [self._format_property(p) for p in properties]
        # Filter out special suggestion objects from properties list to satisfy response schema
        clean_props = [p for p in formatted_props if not p.get("_no_exact_match")]
        state.update({
            "properties": clean_props,
            "search_filters": criteria
        })
        
        # Handle no results with tailored suggestions
        if not clean_props:
            suggestions = self._tailored_suggestions(criteria)
            suggested_areas = self.property_service.suggest_areas(criteria.get("address"))
            state["fallback_context"] = {
                "type": "no_properties",
                "details": {
                    "query": user_query,
                    "filters": criteria,
                    "suggested_areas": suggested_areas,
                    "original_location": original_location_input,
                    "suggestions": suggestions
                }
            }
        else:
            # If we had special suggestion objects originally, surface their message as a refinement hint
            special_msg = None
            for p in formatted_props:
                if p.get("_no_exact_match"):
                    special_msg = p.get("_suggestion_message")
                    break
            if special_msg:
                state["fallback_context"] = {
                    "type": "no_properties",
                    "details": {
                        "query": user_query,
                        "filters": criteria,
                        "suggested_areas": self.property_service.suggest_areas(criteria.get("address")),
                        "original_location": original_location_input,
                        "suggestions": {"budget": special_msg}
                    }
                }
        
        logger.info(f"Found {len(properties)} properties")
        return state
    
    def _get_clarification_prompt(self, query: str) -> str:
        """Get targeted clarification prompt based on query content"""
        q = query.lower()
        
        if "pet" in q:
            return "Do you have cats, dogs, both, or no pets?"
        elif "bed" in q:
            return "How many bedrooms do you need: 1, 2, 3, or 4+?"
        elif "location" in q or "area" in q or "city" in q:
            return "Which city or neighborhood are you looking in?"
        elif "budget" in q or "price" in q or "rent" in q:
            return "What's your monthly budget range?"
        else:
            return "Could you tell me your preferred location, budget, and number of bedrooms?"

    def _looks_non_property(self, q: str) -> bool:
        ql = (q or "").lower()
        non_property_keywords = [
            "tshirt", "t-shirt", "shirt", "jeans", "makeup", "lipstick", "iphone", "android", "laptop",
            "macbook", "headphones", "earbuds", "charger", "grocery", "groceries", "fruits", "vegetables",
            "milk", "perfume", "shampoo", "soap", "toothpaste", "toys", "gaming", "electronics", "camera",
            "television", "tv"
        ]
        return any(k in ql for k in non_property_keywords)

    def _enforce_texas_only(self, criteria: Dict[str, Any]) -> (Dict[str, Any], bool):
        address = str(criteria.get("address") or "").strip()
        if not address:
            return criteria, False
        allowed = {"houston", "dallas", "austin", "san antonio"}
        # If address contains a known Texas city name, allow
        lower_addr = address.lower()
        if any(city in lower_addr for city in allowed):
            return criteria, False
        # Otherwise, redirect to Texas-only options
        # Clear non-Texas location to avoid futile searches
        criteria = dict(criteria)
        criteria["address"] = None
        return criteria, True

    def _tailored_suggestions(self, criteria: Dict[str, Any]) -> Dict[str, str]:
        suggestions: Dict[str, str] = {}
        if criteria.get("rent_exact") or criteria.get("rent_min") or criteria.get("rent_max"):
            target = criteria.get("rent_exact") or criteria.get("rent_max") or criteria.get("rent_min")
            if isinstance(target, (int, float)):
                suggestions["budget"] = (
                    f"I couldn’t find anything at ${int(target)}. Would you like to adjust your budget a little?"
                )
            else:
                suggestions["budget"] = "No matches for this budget. Try widening the range."
        if criteria.get("bedrooms"):
            try:
                br = int(criteria.get("bedrooms"))
                alt = " or ".join([v for v in {br-1, br+1, max(1, br-2)} if isinstance(v, int) and v > 0])
                if alt:
                    suggestions["bedrooms"] = f"No {br}-bed listings match. Would you consider {alt} bedrooms?"
            except Exception:
                suggestions["bedrooms"] = "No exact bedroom match. Consider nearby bedroom counts."
        if criteria.get("pets"):
            suggestions["pets"] = (
                "No listings match this pet policy. Should I try a different pets option, or no pets allowed?"
            )
        if criteria.get("available_date"):
            suggestions["available_date"] = (
                "Nothing for that date. Would you like me to check earlier or later availability?"
            )
        if not suggestions:
            suggestions["general"] = "No exact matches. Try adjusting city, budget, bedrooms, or pet policy."
        return suggestions
    
    def _format_property(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        """Format property for schema compliance"""
        # Pass-through special suggestion objects (no exact match scenarios)
        if prop.get("_no_exact_match"):
            return {
                "_no_exact_match": True,
                "_suggestion_message": str(prop.get("_suggestion_message", ""))
            }
        return {
            "id": str(prop["id"]),
            "address": str(prop["address"]),
            "bedrooms": int(prop["bedrooms"]),
            "rent": float(prop["rent"]),
            "available": str(prop.get("available", True)),
            "pets": str(prop["pets"])
        }