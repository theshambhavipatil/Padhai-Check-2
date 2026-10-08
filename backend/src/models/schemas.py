from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class Verdict(str, Enum):
    TRUE = "True"
    FALSE = "False"
    MISLEADING = "Misleading"
    UNVERIFIED = "Unverified"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    PDF = "pdf"


class VerifyRequest(BaseModel):
    content: str = Field(..., description="Text content or claim to verify")
    content_type: ContentType = Field(default=ContentType.TEXT, description="Type of content")
    file_id: Optional[str] = Field(None, description="ID of uploaded file if any")


class Evidence(BaseModel):
    source: str = Field(..., description="Name of the source (e.g., NTA, CBSE, NCERT)")
    url: Optional[str] = Field(None, description="URL to the official source")
    snippet: str = Field(..., description="Relevant text snippet from the source")
    reliability_score: float = Field(default=0.0, ge=0.0, le=1.0)


class ClaimResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_content: str
    extracted_text: Optional[str] = None
    claim: str
    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    explanation_english: str
    explanation_hinglish: str
    evidence: List[Evidence]
    wellbeing_message: Optional[str] = None
    stress_detected: bool = False
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: ContentType
    extracted_text: str
    message: str


class TrendingClaim(BaseModel):
    claim: str
    verdict: Verdict
    count: int
    first_seen: datetime
    last_seen: datetime
    category: Optional[str] = None


class TrendsResponse(BaseModel):
    trending_claims: List[TrendingClaim]
    total_claims_checked: int
    most_common_category: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class FormattedSection(BaseModel):
    """Individual section in formatted output"""
    type: str = Field(..., description="Type of section: wellbeing, verdict, claim, explanation, evidence, hinglish, error")
    title: str = Field(..., description="Section title with emoji")
    subtitle: Optional[str] = Field(None, description="Optional subtitle")
    content: Optional[str] = Field(None, description="Main content of section")
    items: Optional[List[Dict[str, Any]]] = Field(None, description="List items for sections like evidence")
    icon: Optional[str] = Field(None, description="Section emoji icon")
    confidence: Optional[float] = Field(None, description="Confidence score if applicable")
    color: Optional[str] = Field(None, description="Hex color code for verdict display")


class FormattedSummary(BaseModel):
    """Summary information for quick reference"""
    verdict: str
    confidence: float
    claim: str
    hasStress: bool = False
    evidenceCount: int = 0
    category: Optional[str] = None
    error_type: Optional[str] = None


class FormattedMetadata(BaseModel):
    """Metadata about the verification"""
    id: str
    created_at: Optional[datetime] = None
    original_content: str


class FormattedClaimResult(BaseModel):
    """Structured, formatted claim result for clean display"""
    sections: List[FormattedSection] = Field(..., description="Organized sections with clear separation")
    summary: FormattedSummary = Field(..., description="Quick summary of verdict and claim")
    metadata: FormattedMetadata = Field(..., description="Metadata about the verification")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
