from pathlib import Path

def record_email(email: str) -> str:
    """Use this tool when a user provides an email address, the tool will save it to a file called email.txt in the src/data directory."""

    print(f"Recording email: {email}")
    path = Path("src/data/email.txt")
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
    """Use this tool when a user provides a phone number, the tool will save it to a file called phone.txt in the src/data directory."""

    print(f"Recording phone: {phone}")

    path = Path("src/data/phone.txt")
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