# Backend Integration Guide

## Connecting Padhai Check Frontend to Your FastAPI Backend

### Step 1: Configure Backend URL

Open `/services/api.ts` and update the `BASE_URL`:

```typescript
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

**Options:**
- For local development: `'http://localhost:8000'`
- For production: `'https://api.padhaicheck.com'` or your deployed backend URL
- Using environment variables: Create a `.env` file with `REACT_APP_API_URL=your_backend_url`

### Step 2: Backend Endpoints Required

The frontend expects these FastAPI endpoints:

#### 1. Upload File
```
POST /api/upload
Content-Type: multipart/form-data
Body: { file: File }
Response: { file_url: string }
```

#### 2. Verify Content
```
POST /api/verify
Content-Type: application/json
Body: { 
  text?: string,
  file_urls?: string[]
}
Response: {
  verdict: "True" | "False" | "Misleading" | "Unverified",
  explanation: string,
  evidence: [
    {
      source: string,
      snippet: string,
      url?: string
    }
  ],
  wellbeing_message?: string
}
```

#### 3. Get Trending Claims
```
GET /api/trends
Response: [
  {
    id: string,
    claim: string,
    verdict: "True" | "False" | "Misleading" | "Unverified",
    timestamp: string (ISO format),
    views: number
  }
]
```

#### 4. Get Claim Details
```
GET /api/claim/{id}
Response: {
  id: string,
  claim: string,
  verdict: "True" | "False" | "Misleading" | "Unverified",
  explanation: string,
  evidence: [
    {
      source: string,
      snippet: string,
      url?: string
    }
  ],
  timestamp: string (ISO format),
  wellbeing_message?: string
}
```

### Step 3: CORS Configuration

Your FastAPI backend needs CORS enabled:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # Update with your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 4: Test the Integration

1. Start your FastAPI backend: `uvicorn main:app --reload`
2. Start the frontend: `npm start` or your build command
3. Open the app and test:
   - Upload an image/PDF
   - Ask a question
   - Check if verification results appear
   - View trending claims
   - Check history

### Step 5: Mock Data Fallback

The frontend includes mock data for development. If your backend is unavailable, the app will automatically use mock responses. This allows frontend development to continue independently.

To disable mock fallback, remove the try-catch fallback logic in `/services/api.ts`.

### Example FastAPI Endpoint Implementation

```python
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Evidence(BaseModel):
    source: str
    snippet: str
    url: Optional[str] = None

class VerificationRequest(BaseModel):
    text: Optional[str] = None
    file_urls: Optional[List[str]] = None

class VerificationResponse(BaseModel):
    verdict: str  # "True" | "False" | "Misleading" | "Unverified"
    explanation: str
    evidence: List[Evidence]
    wellbeing_message: Optional[str] = None

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save file and return URL
    file_url = f"/uploads/{file.filename}"
    return {"file_url": file_url}

@app.post("/api/verify", response_model=VerificationResponse)
async def verify_content(request: VerificationRequest):
    # Your AI verification logic here
    return VerificationResponse(
        verdict="True",
        explanation="Your detailed explanation...",
        evidence=[
            Evidence(
                source="Example Source",
                snippet="Example snippet...",
                url="https://example.com"
            )
        ],
        wellbeing_message="Stay hydrated! 💧"
    )

@app.get("/api/trends")
async def get_trends():
    # Return trending claims
    return []

@app.get("/api/claim/{claim_id}")
async def get_claim(claim_id: str):
    # Return claim details
    return {}
```

### Environment Variables

Create a `.env` file in your frontend root:

```
REACT_APP_API_URL=http://localhost:8000
```

### Troubleshooting

1. **CORS errors**: Check CORS middleware configuration in FastAPI
2. **404 errors**: Verify endpoint paths match exactly
3. **Network errors**: Check if backend is running and accessible
4. **Type errors**: Ensure response formats match TypeScript interfaces

### Production Deployment

1. Update `BASE_URL` with production backend URL
2. Ensure CORS allows your production frontend domain
3. Use HTTPS for both frontend and backend
4. Set up proper authentication if needed
5. Configure rate limiting and security headers
