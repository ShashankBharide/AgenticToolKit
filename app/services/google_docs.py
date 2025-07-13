import os
import logging
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import traceback

# These are the permissions your app will ask for.
SCOPES = [
    'https://www.googleapis.com/auth/documents',    # Edit Google Docs
    'https://www.googleapis.com/auth/drive.file'    # Create/edit files in your Drive
]

def get_oauth_creds():
    """
    Handles the OAuth login flow.
    - If you have already logged in before, it loads your saved token.
    - If not, it opens a browser for you to log in and saves the token for next time.
    """
    creds = None
    # If token.pickle exists, load the saved credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, start the login flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)  # Uses your downloaded OAuth credentials
        creds = flow.run_console()  # <-- CHANGE IS HERE
        # Save the credentials for next time
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_google_doc(title, content):
    """
    Creates a Google Doc with the specified title and content using OAuth.
    Returns the URL to edit the document.
    """
    try:
        # Get OAuth credentials (will prompt you to log in the first time)
        creds = get_oauth_creds()
        # Build the Drive and Docs API clients
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # Set up the metadata for the new Google Doc
        file_metadata = {
            'name': title,  # The title of your new doc
            'mimeType': 'application/vnd.google-apps.document'
            # If you want to put it in a folder, add: 'parents': [FOLDER_ID]
        }
        # Create the new Google Doc in your Drive
        doc = drive_service.files().create(body=file_metadata, fields='id').execute()
        doc_id = doc.get('id')  # Get the new document's ID

        # Prepare the request to insert your content at the start of the doc
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
        # Add the content to the doc
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        # Return the link to open your new Google Doc
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except Exception as e:
        # Print and return a friendly error message if something goes wrong
        print(f"Google Docs API error: {e}")
        traceback.print_exc()
        return {"error": "There was a problem creating your Google Doc. Please try again later."}
