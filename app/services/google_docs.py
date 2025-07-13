import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

def get_oauth_creds():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        auth_url, _ = flow.authorization_url(prompt='consent')
        print("Go to the following URL in your browser:", auth_url)
        code = input("Enter the authorization code: ")
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
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
        print(f"Google Docs API error: {e}")
        traceback.print_exc()
        return {"error": "There was a problem creating your Google Doc. Please try again later."}
