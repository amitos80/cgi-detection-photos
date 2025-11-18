import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from forensics import engine

app = FastAPI()

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
        
        results['analysis_duration'] = round(end_time - start_time, 2)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {e}")

    return results

