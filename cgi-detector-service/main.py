import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from forensics import engine

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request to {request.url.path} completed in {process_time:.4f} seconds")
    return response

@app.post("/predict")
async def predict_cgi(file: UploadFile = File(...)):
    """
    Receives an uploaded image, runs it through the forensic analysis engine,
    and returns the results including analysis duration.
    """
    contents = await file.read()

    try:
        start_time = time.time()
        results = engine.run_analysis(contents)
        end_time = time.time()
        
        analysis_duration = round(end_time - start_time, 2)
        results['analysis_duration'] = analysis_duration
        print(f"Image analysis completed in {analysis_duration:.2f} seconds")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {e}")

    return results

@app.post("/feedback")
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

