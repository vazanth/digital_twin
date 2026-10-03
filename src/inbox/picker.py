from pathlib import Path
from inbox.prompt import PICKER
from models.schemas import DraftOption, Inquiry, PickedDraft
from dotenv import load_dotenv
from google import genai

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ME_FILE = PROJECT_ROOT / "data" / "me.txt"

client = genai.Client()


def run_picker(inquiry: Inquiry, drafts: list[DraftOption]) -> PickedDraft:
    me_file = ME_FILE.read_text(encoding="utf-8")

    drafts_section = ""
    for i, d in enumerate(drafts, start=1):
        drafts_section += f"""
        <draft n="{i}" style="{d.style}">
        {d.body}
        </draft>
        """

    contents = f"""<inquiry> 
        Sender Name: {inquiry.sender_name}
        Sender Email: {inquiry.sender_email}
        Subject: {inquiry.subject}
        Message: {inquiry.message}
    </inquiry>
    
    
    <background>{me_file}</background>

    {drafts_section}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config={
            "system_instruction": PICKER,
            "response_mime_type": "application/json",
            "response_schema": PickedDraft,
        },
    )
    if response.text is None:
        raise ValueError("Picker returned empty response")
    # 4. Parse into PickedDraft
    return PickedDraft.model_validate_json(response.text)
