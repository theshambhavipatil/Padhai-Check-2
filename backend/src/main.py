from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from src.api.routes import router
from src.models.schemas import HealthResponse

app = FastAPI(
    title="Padhai Check API",
    description="""
    AI-powered exam claim verification system for Indian students.
    
    Padhai Check helps students verify exam-related information and avoid misinformation.
    Upload screenshots, PDFs, or type messages about exam news to get instant verification.
    
    ## Features
    - **Claim Verification**: Verify claims about JEE, NEET, CBSE, NCERT, UGC, and other Indian education bodies
    - **Multi-format Support**: Accept text, images, and PDF uploads
    - **OCR Processing**: Extract text from screenshots and documents
    - **AI-powered Analysis**: Multiple specialized agents analyze each claim
    - **Bilingual Explanations**: Responses in both English and Hinglish
    - **Wellbeing Support**: Detect student stress and provide supportive messages
    - **Trend Tracking**: Monitor trending rumors and fake news
    
    ## Verdicts
    - **True**: Claim is verified from official sources
    - **False**: Claim is contradicted by official sources
    - **Misleading**: Claim has some truth but is presented deceptively
    - **Unverified**: Cannot confirm or deny; check official sources
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )

