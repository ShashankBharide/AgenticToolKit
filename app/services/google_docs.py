import os
import logging
from google.oauth2 import service_account  # Import Service Account auth class
from googleapiclient.discovery import build

from app import services  # Google API client library

# Define the API scopes we need:
# - documents: allows creating and editing Google Docs
# - drive.file: allows creating files in your Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

# Get the credentials path from the environment variable.
# If the variable is not set, default to 'credentials.json' in current folder.
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

FOLDER_ID = "1NL2GbtP-1UFtk3O820P1kJ9Bxyqhbl4O" # <-- Replace with your real wbw_posts folder ID

def create_google_doc(title, content):
    """
    Creates or updates a Google Doc with the specified title and content in the wbw_posts folder.
    Returns the public URL to edit the document.
    """
    try:
        # Use Service Account credentials.
        # This reads the JSON key file you downloaded from Google Cloud Console.
        # Service Account keys allow server-to-server authentication with no browser.
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH,
            scopes=SCOPES
        )

        # Build the Drive API client using the credentials.
        drive_service = build('drive', 'v3', credentials=creds)

        # Create a new Google Doc in the wbw_posts folder
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [FOLDER_ID]
        }
        doc = drive_service.files().create(body=file_metadata, fields='id').execute()
        doc_id = doc.get('id')

        # Grant permissions using Drive API
        permission = {
            "type": "anyone",
            "role": "reader"
        }
        drive_service.permissions().create(
            fileId=doc_id,
            body=permission
        ).execute()

        # Prepare the request to insert text at the start of the document.
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]

        # Execute the batch update request to insert the text.
        services.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        # Return the URL for the user to open the document in Google Docs.
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except Exception as e:
        # Log any error and return a user-friendly message.
        logging.error(f"Google Docs API error: {e}")
        return {"error": "There was a problem creating your Google Doc. Please try again later."}

def test_service_account_access():
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_PATH,
        scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=creds)
    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents",
        fields="files(id, name)"
    ).execute()
    print("Files in wbw_posts as seen by service account:", results.get('files', []))
