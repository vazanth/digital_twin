import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai._gaos.types.interactions import tool

from inbox.prompt import drafter_instructions
from inbox.tools import get_background
from models.schemas import DraftOption, Inquiry

load_dotenv()

client = genai.Client()


async def generate_draft(inquiry: Inquiry, category, style):
    """Generates a single email reply draft for a given category and persona style."""
    instruction = drafter_instructions(category, style)
    inquiry_text = f"""<inquiry>
    Sender Name: {inquiry.sender_name}
    Sender Email: {inquiry.sender_email}
    Subject: {inquiry.subject}
    Message: {inquiry.message}
    </inquiry>"""

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=inquiry_text,
        config={"system_instruction": instruction, "tools": [get_background]},
    )

    draft_response = {
        "style": style,
        "subject": inquiry.subject,
        "body": response.text.strip() if response.text else "",
    }

    return DraftOption(**draft_response)


async def generate_all_drafts(inquiry: Inquiry, category: str) -> list[DraftOption]:
    """Generates all 3 styles (direct, warm, technical) in parallel using asyncio.gather."""
    styles = ["concise_direct", "warm_relational", "technical_detailed"]

    tasks = [generate_draft(inquiry, category, style) for style in styles]

    drafts = await asyncio.gather(*tasks)

    return drafts
