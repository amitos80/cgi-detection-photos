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

def process_image_base64(b64: str) -> list[float]:
    """
    Decode a base64 image and compute a simple feature vector:
    - per-channel mean and standard deviation (R,G,B) -> 6 values
    - per-channel histogram with 16 bins each -> 48 values
    Total -> 54 floats
    """
    img_bytes = base64.b64decode(b64)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    arr = np.asarray(img).astype(np.float32) / 255.0  # Normalize to 0-1 for consistent feature scaling

    # per-channel mean/std
    means = arr.mean(axis=(0, 1)).tolist()
    stds = arr.std(axis=(0, 1)).tolist()

    # histograms (16 bins per channel), normalized
    hist_bins = 16
    hists = []
    # For histogram, skimage expects integer image (0-255), so convert back for this step
    arr_uint8 = (arr * 255).astype(np.uint8)
    for c in range(3):
        # Use skimage's histogram function, source_range='image' for 0-255 input
        hist, _ = exposure.histogram(arr_uint8[..., c], nbins=hist_bins, source_range='image')
        hist = hist.astype(np.float32)
        if hist.sum() > 0:
            hist = hist / hist.sum()
        hists.extend(hist.tolist())

    feature_vector = means + stds + hists
    return [float(x) for x in feature_vector]

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # read file bytes
    contents = await file.read()
    # optional: save to temp if needed
    unique_filename = str(uuid.uuid4())
    file_path = os.path.join(TEMP_DIR, unique_filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        # Build base64 representation (if you need to pass through APIs)
        b64 = base64.b64encode(contents).decode("ascii")

        # Call the in-Python processor instead of spawning MATLAB
        feature_vector = process_image_base64(b64)

        return {"filename": file.filename, "feature_vector": feature_vector}
    except Exception as e:
        return {"error": "Processing failed", "details": str(e)}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
