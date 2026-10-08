from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import Optional
import uuid

from src.models.schemas import (
    VerifyRequest, ClaimResult, UploadResponse, TrendsResponse,
    ContentType, ErrorResponse, Verdict, FormattedClaimResult
)
from src.utils.file_processor import FileProcessor
from src.utils.storage import storage
from src.agents.orchestrator import orchestrator
from src.utils.output_formatter import OutputFormatter

router = APIRouter(prefix="/api", tags=["Padhai Check API"])


@router.post("/verify", response_model=ClaimResult, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def verify_claim(
    request: Request,
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_id: Optional[str] = Form(None)
):
    """
    Main endpoint for verifying exam-related claims.

    Accepts:
    - Text content directly
    - File upload (image or PDF)
    - Reference to previously uploaded file via file_id
    - JSON payloads with { text?: string, file_ids?: string[] } (added compatibility)

    Returns a comprehensive verification result with verdict, explanation, and evidence.
    """
    extracted_text = None
    original_content = ""

    # If the frontend sent JSON (application/json), parse it and adapt to existing flow
    try:
        content_type = request.headers.get("content-type", "")
    except Exception:
        content_type = ""

    if content_type.startswith("application/json"):
        try:
            payload = await request.json()
        except Exception as e:
            payload = {}

        # Support multiple possible keys for text
        text_value = payload.get("text") or payload.get("content") or payload.get("query")
        file_ids = payload.get("file_ids") or payload.get("file_urls") or payload.get("file_id")

        if isinstance(file_ids, str):
            file_ids = [file_ids]

        if file_ids and isinstance(file_ids, list) and len(file_ids) > 0:
            # Combine extracted text from all provided file ids (if present in storage)
            extracted_parts = []
            for fid in file_ids:
                file_data = storage.get_file(fid)
                if file_data:
                    extracted_parts.append(file_data.get("extracted_text", ""))
            extracted_text = "\n".join([p for p in extracted_parts if p]) if extracted_parts else None

        if text_value:
            original_content = text_value
        elif extracted_text:
            original_content = extracted_text

    # Existing multipart/form-data handling (file uploads and form fields)
    elif file:
        file_bytes = await file.read()
        file_content_type = file.content_type or "application/octet-stream"
        file_name = file.filename or "uploaded_file"

        is_valid, message = FileProcessor.validate_file(file_content_type, len(file_bytes))
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)

        try:
            extracted_text = FileProcessor.process_file(file_bytes, file_content_type)
            # Pass FULL extracted text, not just first 500 chars
            original_content = extracted_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

    elif file_id:
        file_data = storage.get_file(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found. Please upload again.")
        extracted_text = file_data.get("extracted_text", "")
        # Pass FULL extracted text, not truncated version
        original_content = extracted_text

    elif content:
        original_content = content

    else:
        # No content found yet - return a helpful error
        raise HTTPException(status_code=400, detail="Please provide content, file, file_id, or JSON payload with text/file_ids")

    if not original_content and not extracted_text:
        raise HTTPException(status_code=400, detail="No content to verify")

    try:
        result = orchestrator.process_claim(original_content, extracted_text)

        storage.store_claim(result)

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: Agent processing failed: {str(e)}")

        # Return a fallback result instead of failing completely
        # This ensures the user sees SOMETHING instead of a 500 error
        from src.models.schemas import Evidence
        fallback_result = ClaimResult(
            original_content=original_content,
            extracted_text=extracted_text,
            claim=original_content[:200],
            verdict=Verdict.UNVERIFIED,
            confidence=0.0,
            explanation_english=f"Verification failed: {str(e)}. Please ensure GEMINI_API_KEY is set.",
            explanation_hinglish=f"सत्यापन विफल: {str(e)}. कृपया सुनिश्चित करें कि GEMINI_API_KEY सेट है।",
            evidence=[],
            wellbeing_message="We're having technical difficulties. Please try again in a moment.",
            stress_detected=False,
            category="ERROR"
        )
        storage.store_claim(fallback_result)
        return fallback_result


@router.post("/upload", response_model=UploadResponse, responses={400: {"model": ErrorResponse}})
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an image or PDF file for text extraction.

    The extracted text can be used later with the /verify endpoint using the returned file_id.

    Supported formats:
    - Images: JPEG, PNG, WebP
    - Documents: PDF

    Maximum file size: 10MB
    """
    file_bytes = await file.read()
    file_content_type = file.content_type or "application/octet-stream"
    file_name = file.filename or "uploaded_file"

    is_valid, message = FileProcessor.validate_file(file_content_type, len(file_bytes))
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    try:
        extracted_text = FileProcessor.process_file(file_bytes, file_content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from the file. Please ensure the image/PDF contains readable text."
        )

    file_id = str(uuid.uuid4())

    if file_content_type in FileProcessor.ALLOWED_IMAGE_TYPES:
        content_type = ContentType.IMAGE
    else:
        content_type = ContentType.PDF

    storage.store_file(file_id, file_name, file_content_type, extracted_text)

    return UploadResponse(
        file_id=file_id,
        filename=file_name,
        content_type=content_type,
        extracted_text=extracted_text,
        message="File uploaded and text extracted successfully"
    )


@router.get("/claim/{claim_id}", response_model=ClaimResult, responses={404: {"model": ErrorResponse}})
async def get_claim(claim_id: str):
    """
    Retrieve a previously verified claim by its ID.

    Returns the full claim result including verdict, explanation, and evidence.
    """
    claim = storage.get_claim(claim_id)

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return claim


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(limit: int = 10):
    """
    Get trending fake news and misinformation claims.

    Returns the most frequently checked claims, sorted by count.
    Useful for displaying what rumors are currently spreading.
    """
    trending = storage.get_trending_claims(limit=min(limit, 50))
    most_common_category = storage.get_most_common_category()

    return TrendsResponse(
        trending_claims=trending,
        total_claims_checked=storage.total_claims,
        most_common_category=most_common_category
    )


@router.get("/history")
async def get_history(limit: int = 50):
    """
    Get verification history from the backend.

    Returns the most recent verified claims in reverse chronological order.
    This ensures history is server-side and not client-dependent.

    Args:
        limit: Maximum number of history items to return (default: 50, max: 100)

    Returns:
        List of HistoryItem objects with id, query, verdict, timestamp, hasImage
    """
    history = storage.get_history(limit=min(limit, 100))
    return {"history": history}


@router.post("/verify/formatted", response_model=FormattedClaimResult, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def verify_claim_formatted(
    request: Request,
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_id: Optional[str] = Form(None)
):
    """
    Verify a claim and return a clean, well-formatted response with organized sections.

    This endpoint returns the same verification result as /verify but with:
    - Clear section separation (Wellbeing, Verdict, Claim, Explanation, Evidence, etc.)
    - Structured metadata and summary for easy frontend display
    - Color coding and emojis for visual clarity
    - Organized evidence presentation

    Perfect for building a clean, readable UI.
    """
    extracted_text = None
    original_content = ""

    # If the frontend sent JSON (application/json), parse it and adapt to existing flow
    try:
        content_type = request.headers.get("content-type", "")
    except Exception:
        content_type = ""

    if content_type.startswith("application/json"):
        try:
            payload = await request.json()
        except Exception as e:
            payload = {}

        # Support multiple possible keys for text
        text_value = payload.get("text") or payload.get("content") or payload.get("query")
        file_ids = payload.get("file_ids") or payload.get("file_urls") or payload.get("file_id")

        if isinstance(file_ids, str):
            file_ids = [file_ids]

        if file_ids and isinstance(file_ids, list) and len(file_ids) > 0:
            # Combine extracted text from all provided file ids (if present in storage)
            extracted_parts = []
            for fid in file_ids:
                file_data = storage.get_file(fid)
                if file_data:
                    extracted_parts.append(file_data.get("extracted_text", ""))
            extracted_text = "\n".join([p for p in extracted_parts if p]) if extracted_parts else None

        if text_value:
            original_content = text_value
        elif extracted_text:
            original_content = extracted_text

    # Existing multipart/form-data handling (file uploads and form fields)
    elif file:
        file_bytes = await file.read()
        file_content_type = file.content_type or "application/octet-stream"
        file_name = file.filename or "uploaded_file"

        is_valid, message = FileProcessor.validate_file(file_content_type, len(file_bytes))
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)

        try:
            extracted_text = FileProcessor.process_file(file_bytes, file_content_type)
            # Pass FULL extracted text, not just first 500 chars
            original_content = extracted_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

    elif file_id:
        file_data = storage.get_file(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found. Please upload again.")
        extracted_text = file_data.get("extracted_text", "")
        # Pass FULL extracted text, not truncated version
        original_content = extracted_text

    elif content:
        original_content = content

    else:
        # No content found yet - return a helpful error
        raise HTTPException(status_code=400, detail="Please provide content, file, file_id, or JSON payload with text/file_ids")

    if not original_content and not extracted_text:
        raise HTTPException(status_code=400, detail="No content to verify")

    try:
        result = orchestrator.process_claim(original_content, extracted_text)
        storage.store_claim(result)

        # Step 7: Get summary from Summarization Agent
        import logging
        logging.getLogger().info("Step 7: Summarization Agent - Creating concise summary")

        # Prepare claim data for summarization
        claim_data = {
            'main_claim': result.claim,
            'category': result.category or 'Other'
        }
        verdict_data = {
            'verdict': result.verdict
        }

        summary_data = orchestrator.summarization_agent.create_summary(claim_data, verdict_data)

        # Convert to formatted output with summary
        formatted = OutputFormatter.format_claim_result(result.dict(), summary_data)
        return FormattedClaimResult(**formatted)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: Agent processing failed: {str(e)}")

        error_formatted = OutputFormatter.format_error(
            f"Verification failed: {str(e)}. Please ensure GEMINI_API_KEY is set.",
            error_type="processing_error"
        )
        return FormattedClaimResult(**error_formatted)
