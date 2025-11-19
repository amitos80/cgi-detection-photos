import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
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

