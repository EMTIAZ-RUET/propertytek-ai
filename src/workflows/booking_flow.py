"""
Interactive booking flow management for property scheduling
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import re
from src.services.property_details_service import property_details_service
from src.services.property_service import PropertyService

logger = logging.getLogger(__name__)


class BookingFlowManager:
    """Manages the interactive booking flow state and transitions"""
    
    def __init__(self):
        self.flow_steps = {
            'property_search': self._handle_property_search,
            'property_inquiry': self._handle_property_inquiry,
            'slot_selection': self._handle_slot_selection,
            'info_collection': self._handle_info_collection,
            'booking_confirmation': self._handle_booking_confirmation
        }
        self.required_fields_order = ['name', 'email', 'phone', 'pets']
    
    async def process_user_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process user action and determine next step"""
        action_type = state.get('action_type')
        current_step = state.get('current_step', 'property_search')
        
        if action_type == 'inquire':
            return await self._handle_property_inquiry(state)
        elif action_type == 'book_schedule':
            return await self._handle_booking_request(state)
        elif action_type == 'select_slot':
            return await self._handle_slot_selection(state)
        elif action_type == 'provide_info':
            return await self._handle_info_collection(state)
        elif action_type == 'cancel_booking':
            return self._handle_cancel(state)
        else:
            handler = self.flow_steps.get(current_step, self._handle_property_search)
            return await handler(state)
    
    def _next_missing_field(self, user_info: Dict[str, Any]) -> Optional[str]:
        for field in self.required_fields_order:
            if not user_info.get(field):
                return field
        return None
    
    def _prompt_for_field(self, field_name: str) -> str:
        prompts = {
            'name': "What's your full name?",
            'email': "What's your email address?",
            'phone': "What's your phone number?",
            'pets': "Do you have any pets? If yes, please specify."
        }
        return prompts.get(field_name, 'Please provide the requested information.')
    
    def _handle_cancel(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'current_step': 'property_search',
            'response_message': 'Booking canceled. You can start again when ready.',
            'available_slots': [],
            'requires_user_info': False,
            'next_field': None,
            'missing_fields': [],
            'info_prompt': None,
            'appointment_details': None,
            'workflow_complete': False,
            'suggested_actions': ['search_properties', 'book_schedule']
        }
    
    async def _handle_property_search(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'current_step': 'property_search',
            'response_message': 'Here are the available properties. Click "Inquire" for details or "Book Schedule" to view available times.',
            'suggested_actions': ['inquire', 'book_schedule']
        }
    
    async def _handle_property_inquiry(self, state: Dict[str, Any]) -> Dict[str, Any]:
        property_id = state.get('property_id')
        properties = state.get('properties', [])
        
        selected_property = None
        if properties:
            for prop in properties:
                if prop.get('id') == property_id:
                    selected_property = prop
                    break
        else:
            try:
                service = PropertyService()
                all_props = service.get_all_properties()
                for prop in all_props:
                    if str(prop.get('id')) == str(property_id):
                        selected_property = prop
                        properties = all_props
                        break
            except Exception:
                selected_property = None
        
        if not selected_property:
            return {
                'response_message': 'Property not found. Please try again.',
                'current_step': 'property_search'
            }
        
        details = property_details_service.get_property_details(property_id, properties)
        
        return {
            'current_step': 'property_details',
            'response_message': f"Here are the details for {selected_property.get('address', 'this property')}:",
            'property_details': details,
            'suggested_actions': ['book_schedule', 'back_to_search']
        }
    
    async def _handle_booking_request(self, state: Dict[str, Any]) -> Dict[str, Any]:
        property_id = state.get('property_id')
        
        if not property_id:
            return {
                'response_message': 'Please select a property first.',
                'current_step': 'property_search'
            }
        
        available_slots = self._generate_available_slots()
        
        return {
            'current_step': 'slot_selection',
            'response_message': 'Please select an available time slot for your property visit:',
            'available_slots': available_slots,
            'suggested_actions': ['select_slot', 'cancel_booking']
        }
    
    async def _handle_slot_selection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        selected_slot = state.get('selected_slot')
        if not selected_slot:
            return {
                'response_message': 'Please select a time slot.',
                'current_step': 'slot_selection'
            }
        
        user_info = state.get('user_info', {}) or {}
        next_field = self._next_missing_field(user_info)
        if next_field:
            prompt = self._prompt_for_field(next_field)
            return {
                'current_step': 'info_collection',
                'response_message': 'To complete your booking, please provide the following information:',
                'requires_user_info': True,
                'missing_fields': [f for f in self.required_fields_order if not user_info.get(f)],
                'next_field': next_field,
                'info_prompt': prompt,
                'suggested_actions': ['provide_info', 'cancel_booking']
            }
        else:
            return await self._handle_booking_confirmation(state)
    
    def _validate_user_field(self, field_name: str, value: str) -> Dict[str, str]:
        """Validate user input fields with comprehensive checks"""
        errors = {}
        
        if not value or not value.strip():
            errors[field_name] = f"{field_name.title()} is required"
            return errors
            
        value = value.strip()
        
        if field_name == 'name':
            if len(value) < 2:
                errors['name'] = 'Name must be at least 2 characters long'
            elif not value.replace(' ', '').replace('-', '').replace("'", '').isalpha():
                errors['name'] = 'Name can only contain letters, spaces, hyphens, and apostrophes'
            elif len(value) > 100:
                errors['name'] = 'Name is too long (maximum 100 characters)'
                
        elif field_name == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                errors['email'] = 'Please enter a valid email address (e.g., john@example.com)'
            elif len(value) > 254:
                errors['email'] = 'Email address is too long'
                
        elif field_name == 'phone':
            # Remove common formatting characters
            clean_phone = re.sub(r'[\s\-\(\)\.+]', '', value)
            if not clean_phone.isdigit():
                errors['phone'] = 'Phone number can only contain digits and formatting characters'
            elif len(clean_phone) < 10:
                errors['phone'] = 'Phone number must be at least 10 digits'
            elif len(clean_phone) > 15:
                errors['phone'] = 'Phone number is too long'
            # Check for obviously fake numbers
            elif clean_phone in ['1234567890', '0000000000', '1111111111']:
                errors['phone'] = 'Please enter a valid phone number'
                
        elif field_name == 'pets':
            if len(value) > 200:
                errors['pets'] = 'Pet information is too long (maximum 200 characters)'
        
        return errors

    async def _handle_info_collection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_info = state.get('user_info', {}) or {}
        
        # If we have user_info with a new field, validate it
        if state.get('action_type') == 'provide_info':
            # The latest field should be validated
            for field_name in self.required_fields_order:
                if field_name in user_info:
                    field_value = user_info[field_name]
                    validation_errors = self._validate_user_field(field_name, field_value)
                    if validation_errors:
                        return {
                            'current_step': 'info_collection',
                            'response_message': f"Invalid {field_name}: {validation_errors[field_name]}. Please try again:",
                            'requires_user_info': True,
                            'next_field': field_name,
                            'info_prompt': self._prompt_for_field(field_name),
                            'validation_error': True,
                            'suggested_actions': ['provide_info', 'cancel_booking']
                        }
        
        next_field = self._next_missing_field(user_info)
        
        if next_field:
            prompt = self._prompt_for_field(next_field)
            return {
                'current_step': 'info_collection',
                'response_message': prompt,
                'requires_user_info': True,
                'missing_fields': [f for f in self.required_fields_order if not user_info.get(f)],
                'next_field': next_field,
                'info_prompt': prompt,
                'suggested_actions': ['provide_info', 'cancel_booking']
            }
        
        return await self._handle_booking_confirmation(state)
    
    async def _handle_booking_confirmation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        property_id = state.get('property_id')
        selected_slot = state.get('selected_slot')
        user_info = state.get('user_info', {})
        
        appointment_details = {
            'property_id': property_id,
            'slot': selected_slot,
            'user_name': user_info.get('name'),
            'user_email': user_info.get('email'),
            'user_phone': user_info.get('phone'),
            'user_pets': user_info.get('pets', 'Not specified'),
            'created_at': datetime.now().isoformat()
        }
        
        return {
            'current_step': 'booking_complete',
            'response_message': f"Great! Your appointment has been scheduled for {selected_slot}. You'll receive a confirmation SMS shortly.",
            'appointment_details': appointment_details,
            'workflow_complete': True,
            'suggested_actions': ['booking_confirmed', 'new_search']
        }
    
    def _generate_property_details(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'address': property_data.get('address', 'N/A'),
            'bedrooms': property_data.get('bedrooms', 'N/A'),
            'rent': property_data.get('rent', 'N/A'),
            'available_date': property_data.get('available', 'N/A'),
            'pet_policy': property_data.get('pets', 'N/A'),
            'description': f"Beautiful {property_data.get('bedrooms', 'N/A')} bedroom property located at {property_data.get('address', 'this location')}. Monthly rent: ${property_data.get('rent', 'N/A')}. Pet policy: {property_data.get('pets', 'N/A')}.",
            'amenities': ['Air Conditioning', 'Parking', 'Laundry', 'Kitchen Appliances'],
            'contact_info': 'Contact our leasing office for more information.'
        }
    
    def _generate_available_slots(self) -> List[Dict[str, Any]]:
        slots = []
        base_date = datetime.now() + timedelta(days=1)
        for day_offset in range(7):
            date = base_date + timedelta(days=day_offset)
            day_name = date.strftime('%A')
            date_str = date.strftime('%Y-%m-%d')
            slots.extend([
                {
                    'id': f"{date_str}_09:00",
                    'display': f"{day_name}, {date.strftime('%B %d')} at 9:00 AM",
                    'datetime': f"{date_str} 09:00:00",
                    'available': True
                },
                {
                    'id': f"{date_str}_11:00",
                    'display': f"{day_name}, {date.strftime('%B %d')} at 11:00 AM",
                    'datetime': f"{date_str} 11:00:00",
                    'available': True
                },
                {
                    'id': f"{date_str}_14:00",
                    'display': f"{day_name}, {date.strftime('%B %d')} at 2:00 PM",
                    'datetime': f"{date_str} 14:00:00",
                    'available': True
                },
                {
                    'id': f"{date_str}_16:00",
                    'display': f"{day_name}, {date.strftime('%B %d')} at 4:00 PM",
                    'datetime': f"{date_str} 16:00:00",
                    'available': True
                }
            ])
        return slots[:10]


booking_flow_manager = BookingFlowManager()