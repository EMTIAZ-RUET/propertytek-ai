"""
Property Details Service - Handles detailed property information
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PropertyDetailsService:
    """Service for managing detailed property information"""
    
    def __init__(self):
        pass
    
    def get_property_details(self, property_id: str, properties: list) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific property"""
        
        # Find the property
        selected_property = None
        for prop in properties:
            if str(prop.get('id')) == str(property_id):
                selected_property = prop
                break
        
        if not selected_property:
            logger.warning(f"Property not found: {property_id}")
            return None
        
        # Generate comprehensive property details
        details = {
            'basic_info': {
                'id': selected_property.get('id'),
                'address': selected_property.get('address', 'N/A'),
                'bedrooms': selected_property.get('bedrooms', 'N/A'),
                'bathrooms': selected_property.get('bathrooms', 'N/A'),
                'rent': selected_property.get('rent', 'N/A'),
                'available_date': selected_property.get('available', 'N/A'),
                'pet_policy': selected_property.get('pets', 'N/A')
            },
            'description': self._generate_description(selected_property),
            'amenities': self._get_amenities(selected_property),
            'location_info': self._get_location_info(selected_property),
            'lease_terms': self._get_lease_terms(selected_property),
            'contact_info': {
                'leasing_office': '(555) 123-4567',
                'email': 'leasing@propertytek.com',
                'office_hours': 'Mon-Fri 9AM-6PM, Sat 10AM-4PM'
            }
        }
        
        logger.info(f"Generated details for property {property_id}")
        return details
    
    def _generate_description(self, property_data: Dict[str, Any]) -> str:
        """Generate a detailed property description"""
        address = property_data.get('address', 'this location')
        bedrooms = property_data.get('bedrooms', 'N/A')
        rent = property_data.get('rent', 'N/A')
        pets = property_data.get('pets', 'N/A')
        
        description = f"Beautiful {bedrooms} bedroom property located at {address}. "
        description += f"Monthly rent is ${rent}. "
        description += f"Pet policy: {pets}. "
        description += "This property features modern amenities and is conveniently located "
        description += "with easy access to shopping, dining, and transportation."
        
        return description
    
    def _get_amenities(self, property_data: Dict[str, Any]) -> list:
        """Get property amenities"""
        base_amenities = [
            'Air Conditioning',
            'Heating',
            'Kitchen Appliances',
            'Parking Space',
            'Laundry Facilities'
        ]
        
        # Add conditional amenities based on property data
        bedrooms = property_data.get('bedrooms', 0)
        if isinstance(bedrooms, (int, str)) and str(bedrooms).isdigit() and int(bedrooms) >= 2:
            base_amenities.extend(['Walk-in Closet', 'Multiple Bathrooms'])
        
        if property_data.get('pets', '').lower() != 'no pets':
            base_amenities.append('Pet-Friendly')
        
        return base_amenities
    
    def _get_location_info(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get location-specific information"""
        address = property_data.get('address', '')
        
        # Extract city/area from address for location-specific info
        location_info = {
            'neighborhood': 'Residential Area',
            'nearby_amenities': [
                'Grocery Store (0.5 miles)',
                'Public Transportation (0.3 miles)',
                'Park/Recreation (0.8 miles)',
                'Shopping Center (1.2 miles)'
            ],
            'school_district': 'Local School District',
            'walkability_score': '7/10'
        }
        
        # Customize based on address keywords
        if any(keyword in address.lower() for keyword in ['downtown', 'center', 'main']):
            location_info['neighborhood'] = 'Downtown/City Center'
            location_info['walkability_score'] = '9/10'
        elif any(keyword in address.lower() for keyword in ['suburb', 'residential', 'quiet']):
            location_info['neighborhood'] = 'Quiet Residential'
            location_info['walkability_score'] = '6/10'
        
        return location_info
    
    def _get_lease_terms(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get lease terms and conditions"""
        return {
            'lease_length': '12 months (flexible options available)',
            'security_deposit': 'One month rent',
            'application_fee': '$50',
            'utilities_included': 'Water and Trash',
            'utilities_tenant_pays': 'Electricity, Gas, Internet',
            'move_in_requirements': [
                'First month rent',
                'Security deposit',
                'Proof of income (3x rent)',
                'Background check',
                'References'
            ]
        }


# Global property details service instance
property_details_service = PropertyDetailsService()