import os
import logging
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

def get_oauth_creds():
    creds = None
    token_file = 'token.pickle'
    client_secrets_file = 'client_secret.json'

    # Load saved token
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If token invalid or not present, refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.error(f"Token refresh failed: {e}", exc_info=True)
                creds = None  # Force re-auth
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
                # Detect headless env: no DISPLAY or SSH or terminal-only
                if os.environ.get("FLASK_ENV", "").lower() == "prod" or not os.environ.get("DISPLAY"):
                    creds = flow.run_console()
                else:
                    creds = flow.run_local_server(port=0)
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                logging.error(f"OAuth flow failed: {e}", exc_info=True)
                raise e

    return creds

def create_google_doc(title, content):
    try:
        creds = get_oauth_creds()
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }

        doc = drive_service.files().create(body=file_metadata, fields='id').execute()
        doc_id = doc.get('id')

        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except Exception as e:
        logging.error(f"Google Docs API error: {e}")
        print(f"[ERROR] Google Docs API exception: {e}")

        return {"error": "There was a problem creating your Google Doc."}
