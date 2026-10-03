from models.schemas import DraftEmailPayload
import base64
from email.message import EmailMessage
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from models.schemas import DraftEmailPayload

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOKEN_PATH = PROJECT_ROOT / "data" / "token.json"
CREDS_PATH = PROJECT_ROOT / "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def get_gmail_service():
    """Authenticates and returns the Gmail API client service."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif CREDS_PATH.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
            TOKEN_PATH.write_text(creds.to_json())
        else:
            # No credentials.json present yet
            return None
    return build("gmail", "v1", credentials=creds)


def create_gmail_draft(payload: DraftEmailPayload):
    """Creates a draft in Gmail. Returns the draft ID or dry-run message."""
    service = get_gmail_service()

    if not service:
        print("\n--- [DRY-RUN GMAIL DRAFT] ---")
        print(f"To:      {payload.to_email}")
        print(f"Subject: {payload.subject}")
        print(f"Body:\n{payload.body}")
        print("-----------------------------\n")
        return "dry_run_draft_id_12345"

    message = EmailMessage()
    message.set_content(payload.body)
    message["To"] = payload.to_email
    message["Subject"] = payload.subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    draft = (
        service.users()
        .drafts()
        .create(userId="me", body={"message": {"raw": encoded_message}})
        .execute()
    )

    draft_id = draft.get("id")

    print(f"Successfully created Gmail draft (ID: {draft_id}) for {payload.to_email}")

    return draft_id
