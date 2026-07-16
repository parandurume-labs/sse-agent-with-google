"""
Module A: Google Calendar Integration
"""
import os
import datetime
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

class CalendarSync:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticates with Google Calendar API."""
        # For a completely serverless production app, use Service Account credentials.
        # This setup assumes OAuth desktop flow for initial prototyping/testing.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Could not refresh token: {e}")
                    self.creds = None
            
            if not self.creds:
                if os.path.exists(CREDENTIALS_PATH):
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())
                else:
                    logger.warning(f"Google credentials file '{CREDENTIALS_PATH}' not found. Calendar sync will be simulated.")
                    return
        
        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Successfully authenticated with Google Calendar.")
        except Exception as e:
            logger.error(f"Failed to build Calendar service: {e}")

    def add_grant_deadline(self, grant_data, evaluation):
        """
        Adds an all-day event to Google Calendar for the grant deadline.
        Also sets up an email reminder 3 days before.
        """
        if not self.service:
            logger.info(f"[SIMULATION] Would add to Calendar: {grant_data['title']} on {grant_data['due_date']}")
            return True

        event = {
            'summary': f"[마감] {grant_data['title']}",
            'description': f"링크: {grant_data['link']}\n\n추천 사유:\n{evaluation['reason']}",
            'start': {
                'date': grant_data['due_date'],
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                # All-day events need the end date to be the next day
                'date': (datetime.datetime.strptime(grant_data['due_date'], "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                'timeZone': 'Asia/Seoul',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60 * 3}, # 3 days before
                    {'method': 'popup', 'minutes': 24 * 60 * 1}, # 1 day before
                ],
            },
        }

        try:
            created_event = self.service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
            logger.info(f"Event created: {created_event.get('htmlLink')}")
            return True
        except Exception as e:
            logger.error(f"Failed to create calendar event: {e}")
            return False
