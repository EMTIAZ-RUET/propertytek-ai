from twilio.rest import Client
from typing import List, Dict, Any, Optional
from config.settings import settings
import asyncio

class SMSTool:
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.from_number = settings.TWILIO_PHONE_NUMBER
        else:
            self.client = None
            print("Twilio credentials not configured - SMS functionality disabled")
    
    async def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS message with proper validation"""
        
        if not self.client:
            return {
                "success": False,
                "message": "SMS service not configured"
            }
        
        # Validate and format phone number
        if not self.validate_phone_number(to_number):
            return {
                "success": False,
                "message": f"Invalid phone number format: {to_number}. Please use a valid phone number."
            }
        
        try:
            formatted_number = self.format_phone_number(to_number)
            
            # Check if trying to send to same number as from_number
            if formatted_number == self.from_number:
                return {
                    "success": False,
                    "message": "Cannot send SMS to the same number as the sender"
                }
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=formatted_number
            )
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "message": "SMS sent successfully"
            }
            
        except Exception as e:
            error_msg = str(e)
            if "21211" in error_msg:
                return {
                    "success": False,
                    "message": f"Invalid phone number format. Please ensure the number is in correct E.164 format (+1234567890)"
                }
            else:
                return {
                    "success": False,
                    "message": f"Error sending SMS: {error_msg}"
                }
    
    async def send_appointment_confirmation(self, 
                                         phone_number: str,
                                         appointment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send appointment confirmation SMS with comprehensive details"""
        
        message = f"""
PropertyTek Appointment Confirmation

📅 BOOKING DETAILS:
• Client: {appointment_details.get('user_name', 'N/A')}
• Email: {appointment_details.get('user_email', 'N/A')}
• Phone: {appointment_details.get('user_phone', 'N/A')}
• Pets: {appointment_details.get('user_pets', 'Not specified')}

🏠 PROPERTY TOUR:
• Property: {appointment_details.get('property_address', appointment_details.get('property_id', 'N/A'))}
• Date & Time: {appointment_details.get('formatted_date', 'N/A')}
• Appointment ID: {appointment_details.get('id', 'N/A')}

📋 INSTRUCTIONS:
- Arrive 5 minutes early
- Bring valid photo ID
- Reply CANCEL to cancel

Questions? Call (555) 123-4567
        """.strip()
        
        return await self.send_sms(phone_number, message)
    
    async def send_appointment_reminder(self,
                                      phone_number: str,
                                      appointment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send appointment reminder SMS"""
        
        message = f"""
PropertyTek Reminder

Your property tour is tomorrow at {appointment_details.get('formatted_date', 'N/A')}

Property: {appointment_details.get('property_address', 'N/A')}
Appointment ID: {appointment_details.get('id', 'N/A')}

Reply CONFIRM to confirm or RESCHEDULE to change time.
        """.strip()
        
        return await self.send_sms(phone_number, message)
    
    async def send_property_alert(self,
                                phone_number: str,
                                property_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send new property alert SMS"""
        
        message = f"""
New Property Alert - PropertyTek

{property_details.get('address', 'N/A')}
{property_details.get('bedrooms', 0)} bed, {property_details.get('bathrooms', 0)} bath
${property_details.get('rent_price', 0)}/month

Interested? Reply YES to schedule a tour or visit our website.
        """.strip()
        
        return await self.send_sms(phone_number, message)
    
    async def send_bulk_sms(self, 
                          recipients: List[str], 
                          message: str) -> Dict[str, Any]:
        """Send SMS to multiple recipients"""
        
        if not self.client:
            return {
                "success": False,
                "message": "SMS service not configured"
            }
        
        results = []
        successful = 0
        failed = 0
        
        for phone_number in recipients:
            result = await self.send_sms(phone_number, message)
            results.append({
                "phone_number": phone_number,
                "result": result
            })
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "total_sent": len(recipients),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    async def process_incoming_sms(self, from_number: str, message_body: str) -> Dict[str, Any]:
        """Process incoming SMS messages"""
        
        message_lower = message_body.lower().strip()
        
        # Handle common responses
        if message_lower in ["yes", "y", "interested"]:
            return {
                "intent": "schedule_tour",
                "response": "Great! I'd be happy to help you schedule a property tour. What property are you interested in?"
            }
        
        elif message_lower in ["cancel", "cancelled"]:
            return {
                "intent": "cancel_appointment",
                "response": "I can help you cancel your appointment. Please provide your appointment ID or the property address."
            }
        
        elif message_lower in ["confirm", "confirmed"]:
            return {
                "intent": "confirm_appointment", 
                "response": "Thank you for confirming your appointment. We look forward to seeing you!"
            }
        
        elif message_lower in ["reschedule", "change"]:
            return {
                "intent": "reschedule_appointment",
                "response": "I can help you reschedule. Please let me know your preferred new date and time."
            }
        
        elif message_lower in ["stop", "unsubscribe"]:
            return {
                "intent": "unsubscribe",
                "response": "You have been unsubscribed from PropertyTek SMS notifications."
            }
        
        else:
            return {
                "intent": "general_inquiry",
                "response": "Thank you for your message. A PropertyTek representative will respond shortly. For immediate assistance, call (555) 123-4567."
            }
    
    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number for Twilio (E.164 format)"""
        if not phone_number:
            return phone_number
            
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Validate minimum length
        if len(digits) < 10:
            raise ValueError(f"Phone number too short: {phone_number}")
        
        # Apply country rules
        default_cc = (settings.DEFAULT_COUNTRY_CODE or "+1").lstrip('+')

        # Case 1: 10-digit national number (US/Canada style) -> prepend default CC
        if len(digits) == 10:
            return f"+{default_cc}{digits}"

        # Case 2: 11 digits
        if len(digits) == 11:
            # If starts with '1' and default is North America, accept
            if digits.startswith('1') and default_cc == '1':
                return f"+{digits}"
            # If starts with '0', treat as national number with trunk prefix -> replace leading 0 with default CC
            if digits.startswith('0'):
                return f"+{default_cc}{digits[1:]}"
            # Otherwise assume includes country code already
            return f"+{digits}"

        # Case 3: Starts with '0' and length between 10-12 (many countries' local format) -> replace leading 0
        if digits.startswith('0') and 10 <= len(digits) <= 12:
            return f"+{default_cc}{digits[1:]}"

        # Case 4: Already includes country code (12-15 digits)
        if 12 <= len(digits) <= 15:
            return f"+{digits}"

        # Fallback: treat as international with provided digits
        return f"+{digits}"
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format"""
        try:
            formatted = self.format_phone_number(phone_number)
            
            # Basic E.164 validation
            if not formatted.startswith('+'):
                return False
            
            digits = formatted[1:]  # Remove + sign
            
            # Must be all digits after +
            if not digits.isdigit():
                return False
            
            # Must be between 7 and 15 digits (E.164 standard)
            if len(digits) < 7 or len(digits) > 15:
                return False
            
            # Don't allow test numbers or obviously fake numbers
            fake_patterns = [
                '1234567890', '0000000000', '1111111111', '2222222222',
                '3333333333', '4444444444', '5555555555', '6666666666',
                '7777777777', '8888888888', '9999999999', '1234567891',
                '987654321', '234567890', '123456789', '987654320'
            ]
            
            # Check if the last 10 digits match any fake pattern
            last_10_digits = digits[-10:] if len(digits) >= 10 else digits
            if last_10_digits in fake_patterns:
                return False
            
            # Check for sequential or repeated patterns
            if len(last_10_digits) >= 7 and len(set(last_10_digits)) <= 3:  # Too few unique digits
                return False
            
            # Check for obvious test patterns
            if last_10_digits.startswith('555123') or last_10_digits.startswith('555000'):
                return False
            
            return True
            
        except ValueError:
            return False