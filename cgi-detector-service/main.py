import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from forensics import engine, ml_predictor
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request to {request.url.path} completed in {process_time:.4f} seconds")
    return response

def _analyze_single_image(file_data: bytes, filename: str):
    """
    Helper function to analyze a single image and return its results.
    """
    start_time = time.time()
    try:
        results = engine.run_analysis(file_data)
        analysis_duration = round(time.time() - start_time, 2)
        results['analysis_duration'] = analysis_duration
        return {"filename": filename, "prediction": results}
    except Exception as e:
        print(f"ERROR: An exception occurred during analysis of {filename}: {e}")
        import traceback
        traceback.print_exc()
        return {"filename": filename, "error": str(e)}

@app.post("/analyze")
async def predict_cgi(files: list[UploadFile] = File(...)):
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images allowed per request.")

    if len(files) == 1:
        file = files[0]
        contents = await file.read()
        result = _analyze_single_image(contents, file.filename)
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {result['error']}")
        return result
    else:
        with ThreadPoolExecutor() as executor:
            tasks = []
            for file in files:
                contents = await file.read()
                tasks.append(executor.submit(_analyze_single_image, contents, file.filename))
            
            results = []
            for future in tasks:
                results.append(future.result())
        
        # Check for errors in any of the results
        for result in results:
            if "error" in result:
                # If any image failed, return a 500 with details of the first error encountered
                raise HTTPException(status_code=500, detail=f"An error occurred during analysis of {result['filename']}: {result['error']}")
        
        return results


@app.post("/report")
async def receive_feedback(
    file: UploadFile = File(...),
    userCorrection: str = Form(...),
    originalPrediction: str = Form(...)
):
    """
    Receives user feedback on incorrect predictions, including the original image,
    the user's correction, and the original prediction details. This data can be
    used to update or retrain the ML model.
    """
    contents = await file.read()
    print(f"Received feedback for image: {file.filename}")
    print(f"User correction: {userCorrection}")
    print(f"Original prediction: {originalPrediction}")

    # Convert userCorrection to expected label format (e.g., 'cgi' or 'real')
    true_label = "real" if userCorrection == "false_cgi" else "cgi"

    # 1. Save the image and its corrected label to a dataset.
    ml_predictor.save_feedback_image_and_label(contents, true_label)

    # 2. Trigger model retraining with the updated dataset.
    ml_predictor.retrain_with_feedback()

    # 3. Reload the model in the engine to use the newly trained version.
    engine.reload_ml_model() # This function will be added to engine.py

    return {"message": "Feedback received successfully. Model retraining triggered!"}

