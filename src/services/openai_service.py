"""
OpenAI Service for LangGraph Integration
"""

import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Simplified OpenAI service for LangGraph workflows"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze_intent(self, user_query: str) -> Dict[str, Any]:
        """Simplified intent analysis for LangGraph workflow"""
        
        system_prompt = """
        Analyze user intent for PropertyTek platform.
        
        Intent categories:
        - property_search: User wants to find/search properties
        - schedule_tour: User wants to schedule a property viewing
        - confirm_booking: User wants to confirm an appointment
        - ask_question: General questions
        - greeting: Simple greetings and small talk (hi, hello, how are you, what's up)
        - self_introduction: User is introducing themselves (e.g., "I am Emtiaz", "I'm John", "This is Sarah", "My name is Ali"). Do not respond with how-you-are lines for this intent.
        - non_property: User asks about ecommerce products or non-real-estate topics (e.g., cosmetics, phones, laptops, groceries, clothes). Examples of explicit non-property keywords: tshirt, t-shirt, shirt, jeans, dress, shoes, sneakers, cosmetics, makeup, lipstick, foundation, eyeliner, mascara, phone, iphone, android, laptop, macbook, headphones, earbuds, charger, grocery, groceries, fruits, vegetables, milk, perfume, shampoo, soap, toothpaste, toys, gaming, electronics, watch, camera, television, tv.
        
        Classification rules:
        - If the user mentions products, shopping, buying items, or anything clearly not about real estate, return {"intent": "non_property"}.
        - Bedroom counts (e.g., "2 beds", "3 bedrooms", "1br", "studio"), rent/budget mentions, pets policy, or housing terms (apartment, house, condo, rental) indicate property_search.
        - When ambiguous, prefer property_search over non_property if the text can plausibly be a property filter (e.g., just "2 beds").
        - If the user introduces themselves without asking a question (e.g., "I am Emtiaz"), return {"intent": "self_introduction"}.
        
        Return JSON with 'intent' field only. No entity extraction needed.
        IMPORTANT: Treat queries like "give me pets", "give me vacant space", "show apartments", any Texas city mentions, bedroom counts, budget numbers, or pet mentions as property_search.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
                max_tokens=1000,  # Sufficient for intent analysis
                timeout=settings.INTENT_ANALYSIS_TIMEOUT  # Use configured timeout
            )
            
            result = json.loads(response.choices[0].message.content or "{}")
            return {"intent": result.get("intent", "ask_question")}
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return {"intent": "ask_question"}
    
    async def generate_response(self, 
                              user_query: str,
                              intent: str = None,
                              properties: List[Dict[str, Any]] = None,
                              available_slots: List[Dict[str, Any]] = None,
                              appointment_details: Dict[str, Any] = None,
                              error: str = None,
                              fallback_context: Dict[str, Any] = None,
                              messages: List[Dict[str, Any]] = None,
                              search_filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response based on workflow results"""
        
        # Build context
        context_parts = []
        
        if error:
            context_parts.append(f"Error occurred: {error}")
        
        # Handle dynamic fallback scenarios using strategy pattern
        if fallback_context:
            def _need_criteria(details: Dict[str, Any]) -> str:
                missing = details.get("missing") or ["location", "budget", "bedrooms", "pets", "available date"]
                return (
                    "Need more criteria. Ask conversationally for: "
                    + ", ".join(missing)
                )

            def _no_properties_message(details: Dict[str, Any]) -> str:
                orig = (details.get("original_location") or details.get("filters", {}).get("address") or "").strip()
                areas = details.get("suggested_areas") or ["Houston", "Dallas", "Austin", "San Antonio"]
                area_str = ", ".join([str(a) for a in areas])
                # Bedroom alternatives if provided by PropertySearch suggestions
                suggestions = details.get("suggestions") or {}
                br_alt = suggestions.get("bedrooms")
                budget_suggestion = suggestions.get("budget")
                parts = []
                if orig:
                    parts.append(f"I couldn't find any properties in {orig}.")
                else:
                    parts.append("I couldn't find any matching properties.")
                parts.append(f"Let's try refining the search. How about exploring options in {area_str}?")
                if br_alt:
                    parts.append(br_alt)
                if budget_suggestion:
                    parts.append(budget_suggestion)
                parts.append("If you have any specific preferences like budget, bedrooms, or pet policy, feel free to share them for a more tailored search.")
                return " " .join(parts)

            fallback_handlers = {
                "no_properties": _no_properties_message,
                "no_appointments": lambda details: f"No appointment slots available for: {details}",
                "general_failure": lambda details: f"Cannot fulfill request: {details}",
                "need_criteria": _need_criteria,
            }
            
            fallback_type = fallback_context.get("type")
            fallback_details = fallback_context.get("details", {})
            handler = fallback_handlers.get(fallback_type, lambda _: f"Fallback needed: {fallback_context}")
            context_parts.append(handler(fallback_details))
            # Include targeted clarification prompt when provided
            if fallback_type == "need_criteria":
                clarify = fallback_details.get("clarify_prompt")
                if clarify:
                    context_parts.append(f"CLARIFY_PROMPT: {clarify}")
            # Include suggested areas when no properties found
            if fallback_type == "no_properties":
                suggested_areas = fallback_details.get("suggested_areas") or []
                if suggested_areas:
                    context_parts.append("SUGGESTED_AREAS: " + ", ".join([str(a) for a in suggested_areas]))
        elif intent == "non_property":
            # For non-property queries, provide only user-friendly criteria field names (no values)
            criteria = search_filters or {}
            raw_fields = [k for k, v in criteria.items() if v not in (None, "", [], {})]
            # Map internal keys to display names
            field_map = {
                "address": "location",
                "rent_min": "budget",
                "rent_max": "budget",
                "rent_exact": "budget",
                "bedrooms": "bedrooms",
                "pets": "pets",
                "available_date": "available date"
            }
            display_fields_set = set()
            for f in raw_fields:
                mapped = field_map.get(f)
                if mapped:
                    display_fields_set.add(mapped)
            # If no fields detected, show canonical criteria prompts
            if not display_fields_set:
                display_fields = ["location", "budget", "bedrooms", "pets", "available date"]
            else:
                display_fields = sorted(display_fields_set)
            context_parts.append("Non-property query detected.")
            context_parts.append(f"Criteria field names only: {display_fields}")
        elif properties:
            # Check if this is a "no exact match" scenario
            if len(properties) == 1 and properties[0].get('_no_exact_match'):
                context_parts.append("No exact price match found.")
                context_parts.append(f"Suggestion: {properties[0].get('_suggestion_message', '')}")
            else:
                context_parts.append(f"Found {len(properties)} properties:")
                for prop in properties[:5]:  # Show up to 5 properties with full details
                    context_parts.append(
                        f"- {prop.get('address', 'N/A')}: {prop.get('bedrooms', 0)} bedrooms, "
                        f"${prop.get('rent', 0)}/month, Pets: {prop.get('pets', 'N/A')}"
                    )

        # Always include a brief list of detected fields for transparency
        if search_filters is not None:
            non_null_fields = [k for k, v in (search_filters or {}).items() if v not in (None, "", [], {})]
            if non_null_fields:
                context_parts.append("DETECTED_FIELDS: " + ", ".join(non_null_fields))
        
        if available_slots:
            slots_list = "\n".join([f"{i}. {slot.get('formatted_time', 'N/A')}" for i, slot in enumerate(available_slots[:18], 1)])
            context_parts.append(f"Available appointment slots:\n{slots_list}")
        
        if appointment_details:
            context_parts.append(f"Appointment confirmed: {appointment_details.get('formatted_date', 'N/A')}")
        
        context = "\n".join(context_parts) if context_parts else "No specific context available."
        
        system_prompt = """
        You are a helpful property management assistant. Generate natural, contextual responses 
        based on the user's query and situation.
        
        CRITICAL: ONLY use the exact property information provided in the context. 
        NEVER make up property names, addresses, or details that aren't in the provided data.
        
        Guidelines:
        1. Be friendly, professional, and empathetic
        2. Create dynamic, personalized messages based on the specific situation
        3. If showing results, use ONLY the exact addresses and details provided
        4. ALWAYS include available appointment slots in your response when they are provided
        5. For fallback scenarios, craft helpful, specific messages
        5a. If CLARIFY_PROMPT is present, ask EXACTLY that single clarification question.
        5b. If SUGGESTED_AREAS are present, say the requested location has no matches and offer those areas.
        6. If intent is "greeting":
           - Start with a warm, human-like greeting that mirrors their tone (e.g., "I'm doing great, thanks for asking!").
           - ONLY say how you're doing if the user explicitly asked (e.g., "how are you", "how are you doing").
           - In the same message, gently nudge toward property help: invite them to share location, budget, bedrooms, pet policy, or move-in date.
           - Keep it short, friendly, and proactive. Do not list properties.
        6b. If intent is "self_introduction":
           - Acknowledge the name naturally (e.g., "Nice to meet you, Emtiaz!").
           - Do NOT include any "I'm doing well" or similar status lines.
           - Prompt for relevant info to help with the search: location, budget, bedrooms, pets, move-in date.
        7. If intent is "non_property":
           - Generate a dynamic, conversational message (no fixed templates; avoid repeating the same sentence structure).
           - Make it clear you specialize in property search without using the exact phrase "I'm specialized in property search only" or similar canned lines.
           - Do NOT list any properties.
           - ONLY mention the criteria field names (no values). Use friendly names like: location, budget, bedrooms, pets, available date. If none were detected, invite the user to provide any of these fields.
        8. When the context includes CLARIFY_PROMPT, ask EXACTLY that single question and stop.
        
        Property Data Rules:
        - Use EXACT addresses from the provided property list
        - Use EXACT rent amounts, bedroom counts, and pet policies as provided
        - DO NOT create fictional property names like "Sunnydale Apartments"
        - If no properties are provided, say so clearly
        
        Dynamic Fallback Handling:
        - "Need criteria": Ask ONE targeted follow-up question. Prefer the CLARIFY_PROMPT if provided; otherwise choose ONE most relevant field.
        - "No properties found": State clearly there are no matches for the requested location/filters and suggest SUGGESTED_AREAS if provided. If original_location is present, include it. If a bedroom alternative suggestion exists, include it naturally.
        - "No appointment slots": Offer alternative times/dates with helpful scheduling options  
        - "Cannot fulfill request": Politely explain and redirect to available services
        - Always make suggestions relevant to their original request
        
        Message Style:
        - Use conversational, human-like language
        - Be specific about what went wrong and why
        - Offer 2-3 concrete next steps
        - Keep tone positive and solution-focused
        
        IMPORTANT: Return ONLY a valid JSON object with exactly these fields:
        {
          "message": "string with personalized response",
          "suggested_actions": ["action1", "action2", "action3"]
        }
        
        Response Examples:
        - Greeting: "I'm doing great—thanks for asking! I'm here to help with your home search. If you'd like, tell me a city or neighborhood, a monthly budget, how many bedrooms you need, and whether you have pets, and I'll get started."
        - Greeting without explicit "how are you": "Hi there! I can help you find a place. Tell me a city or neighborhood, your budget, bedrooms, and whether you have pets, and I’ll get started."
        - Self-introduction: "Nice to meet you, Emtiaz! I can help you find a place. What city or neighborhood are you looking at, roughly what monthly budget, how many bedrooms, and any pet needs?"
        - Need criteria: "Got it — I can help you find a place. To narrow it down, could you tell me: \n• Which city or neighborhood?\n• Your monthly budget or rent range?\n• Bedrooms needed and any pet requirements?"
        - Properties found: "I found 8 properties in Houston with no pets policy! Here are some options: [list properties with addresses, bedrooms, rent]"
        - No exact price match: Use the exact suggestion message provided in the context
        - No properties: "I couldn't find any properties in India. Let's try refining the search. How about exploring options in Houston, Dallas, Austin, or San Antonio? If you have any specific preferences like budget, bedrooms, or pet policy, feel free to share them for a more tailored search."
        - With appointments: "Here are available slots:\n1. friday 11am-12pm\n2. friday 12pm-1pm"
        - Non-property: "I focus on home rentals. From your message, I can work with these criteria fields: location, budget, bedrooms, pets, available date. Tell me any of those and I’ll help you find places in Texas."
        
        CRITICAL: Ensure valid JSON format. No extra text outside the JSON object.
        """
        
        # Incorporate brief chat history summary
        history_snippets = []
        for m in (messages or [])[-10:]:
            role = m.get("role", "user")
            content = m.get("content", "")
            history_snippets.append(f"{role}: {content}")
        history_block = "\n".join(history_snippets)

        user_prompt = f"""
        Conversation History (last 10):
        {history_block}

        User Query: {user_query}
        Intent: {intent}
        Context: {context}
        
        Generate a helpful response. If available appointment slots are provided in the context, include them in your message.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent JSON
                response_format={"type": "json_object"},
                max_tokens=4000,  # Increased token limit to prevent truncation
                timeout=settings.OPENAI_TIMEOUT  # Use configured timeout
            )
            
            result = response.choices[0].message.content or "{}"
            logger.info(f"OpenAI response content: {result[:200]}...")  # Log first 200 chars
            
            # Check if response was truncated
            if response.usage and response.usage.completion_tokens >= 4000:
                logger.warning("Response may have been truncated - reached max_tokens limit")
            
            parsed_result = json.loads(result)
            
            # Validate required fields using defaults mapping
            field_defaults = {
                "message": "I found some properties for you!",
                "suggested_actions": ["View property details", "Schedule a tour", "Ask questions"]
            }
            
            for field, default_value in field_defaults.items():
                parsed_result.setdefault(field, default_value)
                
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw response: {result}")
            
            # Create response using strategy pattern
            response_strategies = {
                True: {  # Has properties
                    "message": f"I found {len(properties or [])} properties matching your criteria. Check the property cards below for details!",
                    "actions": ["View property details", "Schedule a tour", "Filter by bedrooms"]
                },
                False: {  # No properties
                    "message": "Great — I’ll help you find your place. Could you share your preferred area, your budget or rent range, how many bedrooms you’d like, and whether you have pets? I’ll search right away.",
                    "actions": ["Share preferred area", "Set budget/rent range", "Specify bedrooms/pets"]
                }
            }
            
            strategy = response_strategies[bool(properties)]
            message = strategy["message"]
            actions = strategy["actions"]
                
            return {"message": message, "suggested_actions": actions}
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            
            # Create contextual fallback using strategy pattern
            fallback_strategies = {
                True: {  # Has properties
                    "message": f"I found {len(properties or [])} properties matching your criteria. Please check the property cards for details!",
                    "actions": ["View property details", "Schedule a tour", "Contact us"]
                },
                False: {  # No properties
                    "message": "Great — I’ll help you find your place. Could you share your preferred area, your budget or rent range, how many bedrooms you’d like, and whether you have pets? I’ll search right away.",
                    "actions": ["Share preferred area", "Set budget/rent range", "Specify bedrooms/pets"]
                }
            }
            
            strategy = fallback_strategies[bool(properties)]
            message = strategy["message"]
            actions = strategy["actions"]
                
            return {"message": message, "suggested_actions": actions}