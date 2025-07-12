import os
import logging
from google.oauth2 import service_account  # Import Service Account auth class
from googleapiclient.discovery import build  # Google API client library

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

def create_google_doc(title, content):
    """
    Creates a Google Doc with the specified title and content.
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

        # Build the Docs API client using the credentials.
        service = build('docs', 'v1', credentials=creds)

        # Create a new empty document with the given title.
        doc = service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')  # Extract the document ID

        # Prepare the request to insert text at the start of the document.
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]

        # Execute the batch update request to insert the text.
        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        # Return the URL for the user to open the document in Google Docs.
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except Exception as e:
        # Log any error and return a user-friendly message.
        logging.error(f"Google Docs API error: {e}")
        return {"error": "There was a problem creating your Google Doc. Please try again later."}