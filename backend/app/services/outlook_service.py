from O365 import Account
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

class OutlookService:
    def __init__(self, client_id: str, client_secret: str):
        """Initialize Outlook service with Microsoft Graph credentials"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.account = Account((client_id, client_secret))
        self.calendar = None
    
    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph"""
        try:
            if self.account.authenticate(scopes=['Calendars.Read']):
                self.calendar = self.account.schedule().get_default_calendar()
                return True
            return False
        except Exception as e:
            print(f"Outlook authentication error: {e}")
            return False
    
    def get_meetings_for_week(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Get meetings for a specific week
        
        Args:
            start_date: Start of the week (Monday)
            end_date: End of the week (Friday)
        
        Returns:
            Dictionary with meetings organized by day
        """
        if not self.calendar:
            print("Calendar not initialized. Please authenticate first.")
            return {}
        
        try:
            # Get events for the week
            events = self.calendar.get_events(
                start=start_date,
                end=end_date,
                include_recurring=True
            )
            
            # Organize meetings by day
            meetings_by_day = {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": []
            }
            
            # Map dates to day names
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            
            for event in events:
                # Get event start time
                start_time = event.start
                end_time = event.end
                
                # Calculate duration in hours
                duration = (end_time - start_time).total_seconds() / 3600
                
                # Get day of week (0=Monday, 1=Tuesday, etc.)
                day_of_week = start_time.weekday()
                
                if day_of_week < 5:  # Monday to Friday
                    day_name = day_names[day_of_week]
                    
                    meeting_info = {
                        'subject': event.subject or 'No Subject',
                        'start_time': start_time.strftime('%H:%M'),
                        'end_time': end_time.strftime('%H:%M'),
                        'duration_hours': round(duration, 2),
                        'location': event.location.get('displayName', '') if event.location else '',
                        'organizer': event.organizer.get('emailAddress', {}).get('name', 'Unknown') if event.organizer else 'Unknown',
                        'is_all_day': event.is_all_day,
                        'is_meeting': event.is_meeting if hasattr(event, 'is_meeting') else True
                    }
                    
                    meetings_by_day[day_name].append(meeting_info)
            
            return meetings_by_day
            
        except Exception as e:
            print(f"Error fetching meetings: {e}")
            return {}
    
    def calculate_available_hours(self, meetings_by_day: Dict, work_hours_per_day: int = 8) -> Dict:
        """
        Calculate available working hours after subtracting meeting time
        
        Args:
            meetings_by_day: Dictionary with meetings organized by day
            work_hours_per_day: Total working hours per day
        
        Returns:
            Dictionary with available hours for each day
        """
        available_hours = {}
        
        for day, meetings in meetings_by_day.items():
            total_meeting_hours = sum(
                meeting.get('duration_hours', 0) 
                for meeting in meetings 
                if not meeting.get('is_all_day', False)  # Exclude all-day events
            )
            
            available_hours[day] = max(0, work_hours_per_day - total_meeting_hours)
        
        return available_hours
    
    def get_meeting_summary(self, meetings_by_day: Dict) -> Dict:
        """
        Get a summary of meetings for the week
        
        Args:
            meetings_by_day: Dictionary with meetings organized by day
        
        Returns:
            Summary statistics
        """
        total_meetings = 0
        total_meeting_hours = 0
        meetings_by_priority = {"High": 0, "Medium": 0, "Low": 0}
        
        for day, meetings in meetings_by_day.items():
            total_meetings += len(meetings)
            day_meeting_hours = sum(
                meeting.get('duration_hours', 0) 
                for meeting in meetings 
                if not meeting.get('is_all_day', False)
            )
            total_meeting_hours += day_meeting_hours
        
        return {
            "total_meetings": total_meetings,
            "total_meeting_hours": round(total_meeting_hours, 2),
            "average_meetings_per_day": round(total_meetings / 5, 1),
            "average_meeting_hours_per_day": round(total_meeting_hours / 5, 2)
        } 