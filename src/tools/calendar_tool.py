from typing import Dict, Any
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config.settings import settings

class CalendarTool:
    def __init__(self):
        # Google Calendar API scopes
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        self.calendar_id = 'primary'  # Use primary calendar
        # Credentials path from environment/config
        self.credentials_file = settings.GOOGLE_CALENDAR_CREDENTIALS or ''
        # Token file will be placed alongside the credentials file
        cred_dir = os.path.dirname(self.credentials_file) if self.credentials_file else 'config-json'
        os.makedirs(cred_dir, exist_ok=True)
        self.token_file = os.path.join(cred_dir, 'token.pickle')
        
        # Initialize Google Calendar service
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if self.token_file and os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not getattr(creds, 'valid', False):
            if creds and getattr(creds, 'expired', False) and getattr(creds, 'refresh_token', None):
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                if not self.credentials_file:
                    print("Google Calendar credentials path is not configured. Set GOOGLE_CALENDAR_CREDENTIALS in .env")
                    return
                if not os.path.exists(self.credentials_file):
                    print(f"Credentials file not found: {self.credentials_file}")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"Warning: Failed to write token file at {self.token_file}: {e}")
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            print("Google Calendar API authenticated successfully")
        except Exception as e:
            print(f"Error building Calendar service: {e}")
            self.service = None
    
    async def create_calendar_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Calendar event with provided event data"""
        
        if not self.service:
            return {
                "success": False,
                "message": "Google Calendar service not available",
                "error": "Calendar service not initialized"
            }
        
        try:
            print(f"DEBUG: Creating calendar event with data: {event_data}")
            print(f"DEBUG: Calendar ID: {self.calendar_id}")
            
            # Create the event with sendNotifications=True to send invitations
            event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event_data,
                sendNotifications=True,
                sendUpdates='all'
            ).execute()
            
            print(f"DEBUG: Calendar event created successfully: {event.get('id')}")
            print(f"DEBUG: Event link: {event.get('htmlLink')}")
            print(f"DEBUG: Attendees: {event.get('attendees', [])}")
            
            return {
                "success": True,
                "message": "Calendar event created successfully",
                "event_id": event.get('id'),
                "event_link": event.get('htmlLink'),
                "event_details": {
                    "summary": event.get('summary'),
                    "start": event.get('start'),
                    "end": event.get('end'),
                    "description": event.get('description'),
                    "attendees": event.get('attendees', [])
                }
            }
            
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return {
                "success": False,
                "message": f"Error creating calendar event: {str(e)}",
                "error": str(e)
            }
    
    async def get_fixed_slots_next_day(self, duration_minutes: int = 60) -> list:
        """Get fixed available time slots for the next 3 days"""
        from datetime import datetime, timedelta
        
        slots = []
        for day in range(1, 4):  # Next 3 days
            base_date = (datetime.now() + timedelta(days=day)).replace(hour=11, minute=0, second=0, microsecond=0)
            for hour_offset in range(0, 6):  # 11 AM to 5 PM (6 hours)
                slot_time = base_date + timedelta(hours=hour_offset)
                end_time = slot_time + timedelta(minutes=duration_minutes)
                slots.append({
                    "start_time": slot_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "formatted_time": f"{slot_time.strftime('%A %I%p').lower()}-{end_time.strftime('%I%p').lower()}",
                    "available": True
                })
        
        return slots