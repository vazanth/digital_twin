import json
import uuid
from pathlib import Path


def record_email(email: str) -> str:
    """Use this tool when a user provides an email address, the tool will save it to a file called email.txt in the data directory."""

    print(f"Recording email: {email}")
    path = Path("data/email.txt")
    path.parent.mkdir(parents=True, exist_ok=True)

    emails = set()

    if path.exists():
        emails = set(path.read_text(encoding="utf-8").splitlines())

    if email not in emails:
        with path.open("a", encoding="utf-8") as f:
            f.write("\n" + email + "\n")
    else:
        return "Email already exists in the file."

    return "Email recorded successfully!"


def record_phone_number(phone: str) -> str:
    """Use this tool when a user provides a phone number, the tool will save it to a file called phone.txt in the data directory."""

    print(f"Recording phone: {phone}")

    path = Path("data/phone.txt")
    path.parent.mkdir(parents=True, exist_ok=True)

    phones = set()

    if path.exists():
        phones = set(path.read_text(encoding="utf-8").splitlines())

    if phone not in phones:
        with path.open("a", encoding="utf-8") as f:
            f.write("\n" + phone + "\n")
    else:
        return "Phone number already exists in the file."

    return "Phone number recorded successfully!"


def record_inquiry(inquiry_data: dict) -> str:
    """Save an inquiry from someone who wants to hire, contract, or collaborate."""

    print(f"recording inquiry: {inquiry_data}")

    path = Path("data/inquiry.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "inquiry_id": f"inq_{uuid.uuid4().hex[:8]}",
        "sender_name": inquiry_data["name"],
        "sender_email": inquiry_data["email"],
        "subject": inquiry_data["subject"],
        "message": inquiry_data["message"],
        "status": "pending",
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return "Inquiry recorded. Vasanth will review it personally."
