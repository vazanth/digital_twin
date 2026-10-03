from dotenv import load_dotenv
from inbox.prompt import TRIAGE_CLASSIFIER
from models.schemas import Inquiry, TriageDecision
from google import genai


load_dotenv()

client = genai.Client()


def format_inquiry_for_triage(inquiry: Inquiry) -> str:
    """Wraps untrusted sender content into <inquiry> tags as expected by the prompt."""

    return f"""<inquiry> 
    Sender Name: {inquiry.sender_name}
    Sender Email: {inquiry.sender_email}
    Subject: {inquiry.subject}
    Message: {inquiry.message}
    </inquiry>"""


def run_triage(inquiry: Inquiry) -> TriageDecision:
    """Takes an inquiry dict, calls Gemini with TRIAGE_CLASSIFIER, and returns structured TriageDecision."""

    formatted_input = format_inquiry_for_triage(inquiry)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=formatted_input,
        config={
            "system_instruction": TRIAGE_CLASSIFIER,
            "response_mime_type": "application/json",
            "response_schema": TriageDecision,
        },
    )
    if response.text is None:
        raise ValueError("Gemini returned an empty response")

    return TriageDecision.model_validate_json(response.text)
