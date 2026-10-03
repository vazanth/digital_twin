from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class InquiryCategory(str, Enum):
    RECRUITER = "recruiter"
    FREELANCE = "freelance"
    COLLABORATION = "collaboration"
    OTHER = "other"


extra = "extra"


class UrgencyCategory(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PersonaStyle(str, Enum):
    CONCISE_DIRECT = "concise_direct"
    TECHNICAL_DETAILED = "technical_detailed"
    WARM_RELATIONAL = "warm_relational"


class Inquiry(BaseModel):
    inquiry_id: str
    sender_name: str
    sender_email: str
    subject: str
    message: str
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TriageDecision(BaseModel):
    category: InquiryCategory
    urgency: UrgencyCategory
    confidence_score: float = Field(ge=0.0, le=1.0)
    summary_of_intent: str
    evidence: list[str] = Field(default_factory=list, max_length=2)


class DraftOption(BaseModel):
    style: PersonaStyle
    subject: str
    body: str
    facts_referenced: list[str] = Field(
        default_factory=list,
        description="Grounding facts retrieved via get_background tool",
    )


class PickedDraft(BaseModel):
    selected_style: PersonaStyle
    winning_subject: str
    winning_body: str
    selection_reasoning: str


class DraftEmailPayload(BaseModel):
    to_email: str
    subject: str
    body: str
    label: str = "AI-Drafted"
