import os
import logging
<<<<<<< Updated upstream
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# These are the permissions your app will ask for.
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
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, start the login flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)  # Uses your downloaded OAuth credentials
        creds = flow.run_console()  # Opens a browser for you to log in
        # Save the credentials for next time
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds
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
        creds = flow.run_local_server(port=0)  # Opens a browser for you to log in
        # Save the credentials for next time
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_google_doc(title, content):
    """
    Creates a Google Doc with the specified title and content using OAuth.
    Returns the URL to edit the document.
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
        # Prepare the request to insert your content at the start of the doc
=======
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
>>>>>>> Stashed changes
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
<<<<<<< Updated upstream
        # Add the content to the doc
        docs_service.documents().batchUpdate(
        # Add the content to the doc
        docs_service.documents().batchUpdate(
=======

        # Execute the batch update request to insert the text.
        service.documents().batchUpdate(
>>>>>>> Stashed changes
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

<<<<<<< Updated upstream
        # Return the link to open your new Google Doc
        # Return the link to open your new Google Doc
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except Exception as e:
        
        # Print and return a friendly error message if something goes wrong
        print(f"Google Docs API error: {e}")
=======
        # Return the URL for the user to open the document in Google Docs.
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except Exception as e:
        # Log any error and return a user-friendly message.
        logging.error(f"Google Docs API error: {e}")
>>>>>>> Stashed changes
        return {"error": "There was a problem creating your Google Doc. Please try again later."}
