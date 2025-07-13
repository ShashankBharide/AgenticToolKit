import os
import pickle
import traceback
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes your app needs
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

def get_oauth_creds():
    """
    Handles OAuth authentication for Google APIs.
    - Loads credentials from token.pickle if available and valid.
    - If not, starts the manual OAuth flow:
        1. Prints a URL for you to open in your browser.
        2. You log in and approve, then copy the code Google gives you.
        3. You paste the code into the terminal.
        4. fetch_token exchanges the code for credentials.
        5. Credentials are saved to token.pickle for future use.
    """
    creds = None
    # Try to load existing credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, start OAuth flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        auth_url, _ = flow.authorization_url(prompt='consent')
        print("Go to the following URL in your browser:", auth_url)
        code = input("Enter the authorization code: ")
        # fetch_token exchanges the code for OAuth tokens (access/refresh tokens)
        flow.fetch_token(code=code)
        creds = flow.credentials
        # Save credentials for next time
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_google_doc(title, content):
    """
    Creates a new Google Doc with the given title and content.
    """
    try:
        creds = get_oauth_creds()
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # Create a new Google Doc file
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        doc = drive_service.files().create(body=file_metadata, fields='id').execute()
        doc_id = doc.get('id')

        # Insert the content into the new document
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
        print(f"Google Docs API error: {e}")
        traceback.print_exc()
        return {"error": "There was a problem creating your Google Doc. Please try again later."}
