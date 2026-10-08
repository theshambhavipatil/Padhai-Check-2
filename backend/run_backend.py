#!/usr/bin/env python
"""
Padhai Check Backend Startup Script
This script ensures proper module path handling and starts the FastAPI server
"""
import sys
import os

# Add the current directory to Python path so 'src' can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set default API key if not already set
if not os.environ.get('GEMINI_API_KEY'):
    sys.exit('[ERROR] GEMINI_API_KEY is not set. Copy .env.example, set the key in your shell, and retry.')
print('[INFO] GEMINI_API_KEY is set')

# Now import and run the app
if __name__ == "__main__":
    import uvicorn

    print(f"[INFO] Starting Padhai Check Backend on http://127.0.0.1:5000")
    print(f"[INFO] API Docs available at http://127.0.0.1:5000/docs")

    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        reload_dirs=[os.path.dirname(os.path.abspath(__file__))]
    )

