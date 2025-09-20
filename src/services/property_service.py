"""
LangGraph-based Property Service with LLM Query Generation
"""
import json
import logging
import os
from typing import List, Dict, Optional, Any
from openai import OpenAI
from config.settings import settings
from datetime import date
import calendar

logger = logging.getLogger(__name__)


class PropertyService:
    def __init__(self):
        self.properties = self._load_properties()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def _load_properties(self) -> List[Dict[str, Any]]:
        """Load properties from JSON file"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        data_file = os.path.join(project_root, 'data', 'properties.json')
        self._cache_file = os.path.join(project_root, 'data', 'available_dates_cache.json')
        
        with open(data_file, 'r') as f:
            properties = json.load(f)
        
        logger.info(f"Loaded {len(properties)} properties from file")
        cache = self._load_available_dates_cache()
        normalized = self._normalize_loaded_properties(properties, cache)
        # Save any new cache entries generated during normalization
        self._save_available_dates_cache(cache)
        logger.info(f"Normalized properties to requested schema with available_dates")
        return normalized

    def _normalize_loaded_properties(self, props: List[Dict[str, Any]], cache: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize raw JSON to required schema and synthesize available_dates.

        Target schema per prompt:
        {id, address, bedrooms, rent, pets, available_dates: string[]}
        """
        def normalize_pets(value: Any) -> str:
            text = str(value or "").strip().lower()
            if not text:
                return "no pets allowed"
            if "cats and dogs" in text:
                return "cats and dogs allowed"
            if text == "dogs allowed" or "dogs" in text and "cat" not in text:
                return "dogs only"
            if text == "cats allowed" or "cats" in text and "dog" not in text:
                return "cats only"
            if "no pet" in text:
                return "no pets allowed"
            return value if isinstance(value, str) else "cats and dogs allowed"

        def upcoming_month_labels(n: int = 4) -> List[str]:
            today = date.today()
            labels: List[str] = []
            year = today.year
            month = today.month
            # start from next month
            for i in range(1, n + 1):
                m = month + i
                y = year + (m - 1) // 12
                m = ((m - 1) % 12) + 1
                labels.append(f"{calendar.month_name[m]} {y}")
            return labels

        normalized_list: List[Dict[str, Any]] = []
        for p in props:
            try:
                pid = p.get("id")
                if pid is None:
                    continue
                key = str(pid)
                # Fixed per-listing dates via cache
                if key not in cache:
                    cache[key] = self._generate_available_dates_for_id(pid)
                normalized_list.append({
                    "id": pid,
                    "address": str(p.get("address", "")),
                    "bedrooms": int(p.get("bedrooms", 0)),
                    "rent": int(p.get("rent", 0)),
                    "pets": normalize_pets(p.get("pets")),
                    "available_dates": list(cache.get(key) or [])
                })
            except Exception:
                # Skip malformed entries
                continue
        return normalized_list

    def _load_available_dates_cache(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self._cache_file):
                with open(self._cache_file, 'r') as f:
                    return json.load(f) or {}
        except Exception:
            pass
        return {}

    def _save_available_dates_cache(self, cache: Dict[str, Any]) -> None:
        try:
            os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
            with open(self._cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception:
            # Non-fatal if persisting cache fails
            pass

    def _generate_available_dates_for_id(self, prop_id: int, count: int = 4) -> List[str]:
        # Deterministic per id: start offset cycles across the next months
        today = date.today()
        year = today.year
        month = today.month
        start_offset = (prop_id % 3)  # 0,1,2 to stagger listings
        labels: List[str] = []
        for i in range(1 + start_offset, 1 + start_offset + count):
            m = month + i
            y = year + (m - 1) // 12
            m = ((m - 1) % 12) + 1
            labels.append(f"{calendar.month_name[m]} {y}")
        return labels
    
    async def search_properties_with_llm(self, user_query: str) -> List[Dict[str, Any]]:
        """LLM-driven property search - generates search criteria from natural language"""
        
        # Get sample property structure for LLM context
        sample_property = self.properties[0] if self.properties else {}
        
        system_prompt = f"""
        You are a property search assistant. Extract search criteria from user queries.
        
        Property structure: {json.dumps(sample_property, indent=2)}
        
        Extract these search criteria from user input:
        - address: location/city/area (partial match)
        - rent_min: minimum rent amount
        - rent_max: maximum rent amount  
        - bedrooms: number of bedrooms
        - pets: pet policy (No Pets, Dogs, Cats, Cats and Dogs)
        - available_date: when they need the property
        
        Return JSON with extracted criteria. Use null for missing values.
        Examples:
        - "2 bedroom in Austin under $1500" → {{"bedrooms": 2, "address": "Austin", "rent_max": 1500}}
        - "pet friendly apartments" → {{"pets": "Dogs"}}
        - "cheap places downtown" → {{"address": "downtown"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            criteria = json.loads(response.choices[0].message.content or "{}")
            logger.info(f"LLM extracted criteria: {criteria}")
            
            # Execute search with extracted criteria
            return self._execute_search(criteria)
            
        except Exception as e:
            logger.error(f"Error in LLM search: {e}")
            return []

    async def extract_search_criteria(self, user_query: str) -> Dict[str, Any]:
        """Extract property search criteria from free text without running a search"""
        sample_property = self.properties[0] if self.properties else {}
        system_prompt = f"""
        Extract property search criteria from user queries. Return JSON with keys: address, rent_min, rent_max, rent_exact, bedrooms, pets, available_date.

        CRITICAL RULES for available_date:
        - Only set available_date if the user provides a real date or a month name.
        - Accept formats like: "Jan", "February", "18.03.25", "18/03/2025", "2025-03-18".
        - Do NOT set available_date for words like "vacant", "available now", or "now".

        CRITICAL RULES for budget/rent extraction:
        - "3000" or "i want 3000" → rent_exact: 3000 (user wants properties that cost exactly this price)
        - "under 3000" or "below 3000" → rent_max: 2999 (properties less than 3000)
        - "over 2000" or "above 2000" → rent_min: 2001 (properties more than 2000)
        - "between 1500 and 2500" → rent_min: 1500, rent_max: 2500
        - "around 2000" → rent_min: 1900, rent_max: 2100 (±5%)

        Examples:
        - "i want 3000" → {{"rent_exact": 3000}}
        - "property under 3000" → {{"rent_max": 2999}}
        - "property above 3000" → {{"rent_min": 3001}}
        - "2 bedroom in Austin under $1500" → {{"bedrooms": 2, "address": "Austin", "rent_max": 1499}}
        - "house over 2000" → {{"rent_min": 2001}}
        - "3 bed apartment around 2500" → {{"bedrooms": 3, "rent_min": 2400, "rent_max": 2600}}
        - "pet friendly apartments" → {{"pets": "Dogs"}}
        - "downtown places" → {{"address": "downtown"}}

        Property structure: {json.dumps(sample_property, indent=2)}
        """
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            criteria = json.loads(response.choices[0].message.content or "{}")
            # Post-validate available_date: only month names or date-like values allowed
            available_date = criteria.get("available_date")

            import re
            month_re = re.compile(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b", re.IGNORECASE)
            date_like_re = re.compile(r"^(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}-\d{2}-\d{2})$")
            invalid_keywords = {"vacant", "available now", "now", "immediate", "immediately", "available"}

            def _is_valid_available_date(text: Any) -> bool:
                if not isinstance(text, str):
                    return False
                t = text.strip()
                if not t:
                    return False
                if t.lower() in invalid_keywords:
                    return False
                return bool(month_re.search(t) or date_like_re.search(t))

            if not _is_valid_available_date(available_date):
                available_date = None

            # STRICT bedrooms rule: accept bedrooms ONLY if a number is explicitly specified by the user
            bedrooms_value = criteria.get("bedrooms")
            q = (user_query or "").lower()
            # Detect a numeric bedroom mention near bedroom keywords
            has_numeric_bedrooms_phrase = bool(re.search(r"\b(\d+)\s*(bed|beds|bedroom|bedrooms|br)\b", q))
            # Coerce bedrooms to int when valid, otherwise None
            def _normalize_bedrooms(raw: Any) -> Optional[int]:
                if isinstance(raw, int):
                    return raw
                if isinstance(raw, str) and raw.strip().isdigit():
                    return int(raw.strip())
                return None
            normalized_bedrooms = _normalize_bedrooms(bedrooms_value)
            if not has_numeric_bedrooms_phrase:
                # User did not specify a number alongside bedroom keywords; ignore any LLM guess
                normalized_bedrooms = None

            # Normalize keys and ensure all expected keys exist
            normalized = {
                "address": criteria.get("address"),
                "rent_min": criteria.get("rent_min"),
                "rent_max": criteria.get("rent_max"),
                "rent_exact": criteria.get("rent_exact"),
                "bedrooms": normalized_bedrooms,
                "pets": criteria.get("pets"),
                "available_date": available_date
            }
            logger.info(f"LLM extracted criteria (no search): {normalized}")
            return normalized
        except Exception as e:
            logger.error(f"Error extracting criteria: {e}")
            return {"address": None, "rent_min": None, "rent_max": None, "rent_exact": None, "bedrooms": None, "pets": None, "available_date": None}
    
    def _execute_search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute search on JSON data using extracted criteria"""
        results = []
        
        for prop in self.properties:
            if self._matches_criteria(prop, criteria):
                results.append(prop)
        
        # Handle no results for exact rent match
        if len(results) == 0 and criteria.get('rent_exact'):
            # Check if there are properties under or above this price
            exact_price = criteria['rent_exact']
            under_count = len([p for p in self.properties if p['rent'] < exact_price])
            above_count = len([p for p in self.properties if p['rent'] > exact_price])
            
            # Create a special result with suggestion message
            suggestion_message = self._generate_exact_price_suggestion(exact_price, under_count, above_count)
            results = [{'_no_exact_match': True, '_suggestion_message': suggestion_message}]
            
        # Limit to 5 results and add dynamic refinement message if more found
        elif len(results) > 5:
            total_found = len(results)
            results = results[:5]
            # Generate dynamic message based on missing criteria
            if results:
                results[0]['_search_message'] = self._generate_refinement_message(total_found, criteria)
        
        logger.info(f"Found {len(results)} properties, returning {len(results)} results")
        return results

    def search_with_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public method to search using provided criteria without LLM extraction"""
        return self._execute_search(criteria or {})
    
    def _generate_exact_price_suggestion(self, exact_price: int, under_count: int, above_count: int) -> str:
        """Generate suggestion message when no exact price match is found"""
        suggestions = []
        if under_count > 0:
            suggestions.append(f"under ${exact_price}")
        if above_count > 0:
            suggestions.append(f"above ${exact_price}")
        
        if suggestions:
            suggestion_text = " or ".join(suggestions)
            return f"We couldn't find properties at exactly ${exact_price}. Try searching for properties {suggestion_text}, or specify other criteria like location, bedrooms, or pet policy to find more options."
        else:
            return f"We couldn't find properties at exactly ${exact_price}. Try specifying other criteria like location, bedrooms, or pet policy to find available options."

    def _generate_refinement_message(self, total_found: int, criteria: Dict[str, Any]) -> str:
        """Generate LLM-powered refinement message based on missing search criteria"""
        try:
            missing_filters = []
            if not criteria.get('bedrooms'): missing_filters.append('bedrooms')
            if not criteria.get('pets'): missing_filters.append('pet policy')
            if not criteria.get('rent_min') and not criteria.get('rent_max'): missing_filters.append('rent range')
            if not criteria.get('address'): missing_filters.append('location')
            
            prompt = f"Generate a helpful, concise message for property search results. Found {total_found} properties, showing 5. Missing criteria: {missing_filters}. Keep it under 20 words and friendly."
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip()
        except:
            return f"Showing 5 of {total_found} results. Try being more specific to find exactly what you need."

    def _matches_criteria(self, prop: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if property matches LLM-extracted criteria"""
        
        # Address matching (partial, case-insensitive)
        if criteria.get('address'):
            if criteria['address'].lower() not in prop['address'].lower():
                return False
        
        # Rent matching - exact, min, max logic
        if criteria.get('rent_exact'):
            # Exact match only
            if prop['rent'] != criteria['rent_exact']:
                return False
        else:
            # Range matching
            if criteria.get('rent_min') and prop['rent'] < criteria['rent_min']:
                return False
            if criteria.get('rent_max') and prop['rent'] > criteria['rent_max']:
                return False
        
        # Bedroom matching
        if criteria.get('bedrooms') and prop['bedrooms'] != criteria['bedrooms']:
            return False
        
        # Pet policy matching
        if criteria.get('pets'):
            if criteria['pets'].lower() not in prop['pets'].lower():
                return False
        
        # Available date matching (simplified - assume all properties available)
        # In real implementation, this would check actual availability dates
        
        return True
    
    def get_all_properties(self) -> List[Dict[str, Any]]:
        """Get all properties"""
        return self.properties

    def list_distinct_areas(self) -> List[str]:
        """Return distinct area/location strings from property addresses."""
        areas: List[str] = []
        for prop in self.properties:
            address = str(prop.get('address', '')).strip()
            if not address:
                continue
            # Heuristic: area is text before first comma, or full address if no comma
            area = address.split(',')[0].strip()
            if area and area not in areas:
                areas.append(area)
        return areas

    def suggest_areas(self, desired_area: str, limit: int = 5) -> List[str]:
        """Suggest up to 'limit' areas from data when a requested area has no matches."""
        desired = (desired_area or '').lower().strip()
        areas = self.list_distinct_areas()
        # Prefer areas that start with the same first letter(s)
        def score(a: str) -> int:
            al = a.lower()
            if desired and al.startswith(desired[:1]):
                return 0
            return 1
        areas_sorted = sorted(areas, key=score)
        return areas_sorted[:limit]
