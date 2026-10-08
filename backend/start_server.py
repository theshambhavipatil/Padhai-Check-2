#!/usr/bin/env python
"""
Padhai Check Backend - Direct Startup Script
Handles module path setup and starts FastAPI
"""
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add it to Python path so 'src' package can be found
sys.path.insert(0, script_dir)

# Set GEMINI API Key from environment or use default
if not os.environ.get('GEMINI_API_KEY'):
    sys.exit('[ERROR] GEMINI_API_KEY is not set. Set it in your shell before starting the server.')

print(f"[INFO] Starting Padhai Check Backend")
print(f"[INFO] Python path: {script_dir}")
print(f"[INFO] GEMINI_API_KEY: {'SET' if os.environ.get('GEMINI_API_KEY') else 'NOT SET'}")
print()

try:
    # Import the FastAPI app from src.main
    from src.main import app
    print("[✓] Successfully imported main app")

    # Import and run uvicorn
    import uvicorn
    print("[✓] Starting Uvicorn server on http://127.0.0.1:5000")
    print("[✓] Docs available at http://127.0.0.1:5000/docs")
    print()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        reload=False
    )

except Exception as e:
    print(f"[✗] ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
