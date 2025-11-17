from fastapi import FastAPI, UploadFile, File, HTTPException
from forensics import engine

app = FastAPI()

@app.post("/predict")
async def predict_cgi(file: UploadFile = File(...)):
    """
    Receives an uploaded image, runs it through the forensic analysis engine,
    and returns the results.
    """
    # 1. Read image bytes
    contents = await file.read()

    # 2. Run the analysis
    try:
        results = engine.run_analysis(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {e}")

    # 3. Return the results
    return results

