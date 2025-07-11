import os
import logging
from google.oauth2 import service_account  # For authenticating with service account credentials
from googleapiclient.discovery import build  # For accessing Google APIs (Docs and Drive)

# Define the OAuth scopes needed:
# - 'documents': to create and edit Google Docs
# - 'drive.file': to create and manage files in Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

# Use an environment variable for the credentials file path, or fallback to 'credentials.json'
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

def create_google_doc(title, content):
    """
    Creates or updates a Google Doc with the specified title and content.
    If a doc with this title exists, it updates it.
    Otherwise, it creates a new doc.
    Returns the URL to edit the document.
    """
    try:
        # Authenticate using service account credentials
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH,
            scopes=SCOPES
        )

        # Build clients for Drive and Docs APIs
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # Query Drive for an existing Google Doc with the specified title
        query = (
            f"name='{title}' "
            "and mimeType='application/vnd.google-apps.document' "
            "and trashed=false"
        )
        results = drive_service.files().list(
            q=query,
            fields="files(id, name, createdTime)",  # Only retrieve id, name, and created time
            orderBy="createdTime desc"  # Sort so the most recently created doc comes first
        ).execute()
        files = results.get('files', [])

        if files:
            # If a document was found, use the most recently created one
            doc_id = files[0]['id']
            logging.info(f"Found existing doc '{title}' (ID: {doc_id}), updating.")
        else:
            # Otherwise, create a new document with the specified title
            doc = docs_service.documents().create(body={'title': title}).execute()
            doc_id = doc.get('documentId')
            logging.info(f"Created new doc '{title}' (ID: {doc_id}).")

            # Grant read access to anyone with the link
            drive_service.permissions().create(
                fileId=doc_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()

        # Retrieve the document's current content structure
        doc_content = docs_service.documents().get(documentId=doc_id).execute()
        body_content = doc_content.get('body', {}).get('content', [])

        # Determine the end index of the content to know how much to delete
        if body_content:
            end_index = body_content[-1].get('endIndex', 1)
        else:
            end_index = 1

        # Build requests to clear and replace the content
        requests = []
        if end_index > 1:
            # If there is existing content, delete everything from start to end
            requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_index
                    }
                }
            })
        # Insert the new content at the beginning of the document
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        })

        # Send the batch update request to Google Docs API
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        # Return the URL to edit the document
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except Exception as e:
        # Log the full stack trace for debugging
        logging.exception("Error creating or updating Google Doc:")
        # Return an error dictionary to the caller
        return {"error": "There was a problem creating or updating your Google Doc."}
