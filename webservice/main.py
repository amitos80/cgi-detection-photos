# python
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
import base64
import io
import numpy as np
from PIL import Image
from skimage import exposure

app = FastAPI()

# Get the absolute path to the directory containing main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(current_dir, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

static_dir = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, 'index.html'))

import httpx

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    
    # Get the service URL from environment variables, with a fallback for local dev
    cgi_detector_url = os.environ.get("PYTHON_SERVICE_URL", "http://localhost:8001/predict")

    files = {'file': (file.filename, await file.read(), file.content_type)}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(cgi_detector_url, files=files, timeout=300.0)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # The cgi-detector-service returns a JSON response with the analysis
            prediction_data = response.json()
            
            return {
                "filename": file.filename,
                "prediction": prediction_data
            }

        except httpx.RequestError as e:
            # Handle connection errors, timeouts, etc.
            return {"error": "Could not connect to the analysis service", "details": str(e)}
        except Exception as e:
            # Handle other exceptions, including non-JSON responses
            return {"error": "An unexpected error occurred", "details": str(e)}
