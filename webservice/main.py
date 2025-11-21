from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import json
from datetime import datetime
import fcntl # For file locking on Unix-like systems
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request to {request.url.path} completed in {process_time:.4f} seconds")
    return response


# Get the absolute path to the directory containing main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up to the project root to define the feedback directory
project_root = os.path.dirname(current_dir)
FEEDBACK_DIR = os.path.join(project_root, "feedback_data")
FEEDBACK_IMAGES_DIR = os.path.join(FEEDBACK_DIR, "images")
REPORTS_FILE = os.path.join(FEEDBACK_DIR, "reports.json")

os.makedirs(FEEDBACK_IMAGES_DIR, exist_ok=True)

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

    contents = await file.read()
    files = {'file': (file.filename, contents, file.content_type)}

    async with httpx.AsyncClient() as client:
        try:
            # Use the streaming API to get the response more actively
            async with client.stream("POST", cgi_detector_url, files=files, timeout=300.0) as response:
                response.raise_for_status()
                # Read the entire response body at once
                response_body = await response.aread()
            
            # Manually decode the JSON
            prediction_data = json.loads(response_body)
            
            return {
                "filename": file.filename,
                "prediction": prediction_data
            }

        except httpx.RequestError as e:
            return JSONResponse(status_code=503, content={"error": "Could not connect to the analysis service", "details": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": "An unexpected error occurred", "details": str(e)})

@app.post("/report")
async def report_incorrect_result(
    file: UploadFile = File(...),
    userCorrection: str = Form(...),
    originalPrediction: str = Form(...)
):
    
    # Get the service URL from environment variables, with a fallback for local dev
    cgi_detector_feedback_url = os.environ.get("PYTHON_SERVICE_URL_FEEDBACK", "http://localhost:8001/feedback")

    contents = await file.read()
    files = {'file': (file.filename, contents, file.content_type)}
    data = {
        'userCorrection': userCorrection,
        'originalPrediction': originalPrediction
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(cgi_detector_feedback_url, files=files, data=data, timeout=300.0)
            response.raise_for_status()
            
            return response.json()

        except httpx.RequestError as e:
            return JSONResponse(status_code=503, content={"error": "Could not connect to the feedback service", "details": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": "An unexpected error occurred", "details": str(e)})
