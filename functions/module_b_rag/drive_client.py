"""
Module B: Google Drive API Integration for RAG Wiki
"""
import os
import io
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

# Combined scopes for both Calendar and Drive Readonly
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/drive.readonly'
]

class DriveClient:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticates with Google Drive API."""
        token_path = 'token.json'
        # Check in the parent directory if running inside module_b_rag
        if not os.path.exists(token_path) and os.path.exists('../token.json'):
            token_path = '../token.json'
            
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Could not refresh token: {e}")
                    self.creds = None
            
            if not self.creds:
                creds_file = CREDENTIALS_PATH
                if not os.path.exists(creds_file) and os.path.exists('../' + CREDENTIALS_PATH):
                    creds_file = '../' + CREDENTIALS_PATH
                
                if os.path.exists(creds_file):
                    flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    with open(token_path, 'w') as token:
                        token.write(self.creds.to_json())
                else:
                    logger.warning("Google credentials file not found. Drive sync will be simulated.")
                    return
        
        try:
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("Successfully authenticated with Google Drive.")
        except Exception as e:
            logger.error(f"Failed to build Drive service: {e}")

    def fetch_wiki_files(self) -> dict:
        """
        Fetches all markdown files from the '02_Knowledge_Wiki' folder in Google Drive.
        Returns a dictionary mapping filename to file content (string).
        Falls back to local file system if Google Drive API is not authenticated or fails.
        """
        local_wiki_path = os.getenv(
            "LOCAL_WIKI_PATH",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "SSE_Agent_Workspace", "02_Knowledge_Wiki"))
        )
        
        # If Drive service is not available, default to local fallback
        if not self.service:
            logger.info("Drive service not initialized. Using local fallback.")
            return self._fetch_local_wiki(local_wiki_path)

        try:
            # 1. Find the '02_Knowledge_Wiki' folder
            query = "mimeType = 'application/vnd.google-apps.folder' and name = '02_Knowledge_Wiki' and trashed = false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            folders = results.get('files', [])

            if not folders:
                logger.warning("Folder '02_Knowledge_Wiki' not found in Drive. Using local fallback.")
                return self._fetch_local_wiki(local_wiki_path)

            folder_id = folders[0]['id']
            logger.info(f"Found '02_Knowledge_Wiki' folder in Drive (ID: {folder_id})")

            # 2. List all markdown files in the folder
            file_query = f"'{folder_id}' in parents and trashed = false"
            file_results = self.service.files().list(q=file_query, fields="files(id, name, mimeType)").execute()
            files = file_results.get('files', [])

            wiki_docs = {}
            for f in files:
                filename = f['name']
                # Accept markdown or plain text files
                if filename.endswith('.md') or f['mimeType'] in ['text/markdown', 'text/plain']:
                    file_id = f['id']
                    logger.info(f"Downloading file from Drive: {filename} ({file_id})")
                    
                    # Download content
                    request = self.service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                    
                    content = fh.getvalue().decode('utf-8', errors='ignore')
                    wiki_docs[filename] = content

            if not wiki_docs:
                logger.warning("No markdown files found in Google Drive folder. Using local fallback.")
                return self._fetch_local_wiki(local_wiki_path)

            return wiki_docs

        except Exception as e:
            logger.error(f"Error fetching wiki files from Google Drive: {e}. Falling back to local files.")
            return self._fetch_local_wiki(local_wiki_path)

    def _fetch_local_wiki(self, path) -> dict:
        """Helper to read files from local directory."""
        wiki_docs = {}
        if not os.path.exists(path):
            logger.error(f"Local wiki path '{path}' does not exist.")
            return wiki_docs

        logger.info(f"Reading wiki files from local path: {path}")
        for file in os.listdir(path):
            if file.endswith('.md'):
                file_path = os.path.join(path, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        wiki_docs[file] = f.read()
                except Exception as e:
                    logger.error(f"Error reading local file {file}: {e}")
        return wiki_docs

if __name__ == "__main__":
    # Test authentication and fetching
    client = DriveClient()
    docs = client.fetch_wiki_files()
    print(f"Fetched {len(docs)} documents.")
    for name, content in docs.items():
        print(f"--- {name} ---")
        print(content[:100] + "...\n")
