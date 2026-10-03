import asyncio
import json
from pathlib import Path

from inbox.drafter import generate_all_drafts
from inbox.picker import run_picker
from inbox.sender import create_gmail_draft
from inbox.triage import run_triage
from models.schemas import DraftEmailPayload, DraftOption, Inquiry, PickedDraft

PROJECT_ROOT = Path(__file__).resolve().parents[2]
inquiries_path = PROJECT_ROOT / "data" / "inquiry.jsonl"


def load_pending_inquiries() -> list[Inquiry]:
    """Reads inquiry.jsonl and returns only rows where status == 'pending'."""
    pending_items = []

    with inquiries_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)

            print("status:", record.get("status"))

            if record.get("status") == "pending":
                inquiry = Inquiry.model_validate(record)
                pending_items.append(inquiry)

    return pending_items


def update_pending_items(inquiry_id: str, new_status: str):
    """Updates the status and metadata of a specific inquiry in inquiry.jsonl."""

    if not inquiries_path.exists():
        return

    records = []

    with inquiries_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line.strip()))

    for r in records:
        if r.get("inquiry_id") == inquiry_id:
            r["status"] = new_status

    with inquiries_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


async def process_inbox():
    pending_inquiries: list[Inquiry] = load_pending_inquiries()
    print(f"Found {len(pending_inquiries)} pending inquiries.")

    for pending in pending_inquiries:
        item_id = pending.inquiry_id
        decision = run_triage(pending)

        print(f"Category:   {decision.category.value}")
        print(f"Urgency:    {decision.urgency.value}")
        print(f"Confidence: {decision.confidence_score}")
        print(f"Summary:    {decision.summary_of_intent}")

        if decision.category.value != "other":
            drafts: list[DraftOption] = await generate_all_drafts(
                pending, decision.category.value
            )
            result: PickedDraft = run_picker(pending, drafts)

            email_payload = DraftEmailPayload(
                to_email=pending.sender_email,
                subject=result.winning_subject or f"Re: {pending.subject}",
                body=result.winning_body,
            )

            draft_id = create_gmail_draft(email_payload)

            print(f"Success! Gmail Draft ID: {draft_id}")

            update_pending_items(inquiry_id=pending.inquiry_id, new_status="triaged")
        elif decision.category.value == "other":
            print(f"Skipping item {item_id} (Category: other)")
            update_pending_items(inquiry_id=pending.inquiry_id, new_status="triaged")


if __name__ == "__main__":
    asyncio.run(process_inbox())
