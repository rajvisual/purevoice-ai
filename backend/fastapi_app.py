"""
FastAPI Production Implementation for InstaEdit Audio/Video Denoiser
===================================================================
Run with: uvicorn backend.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .denoiser_engine import InstaAudioDenoiser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="InstaEdit AI Audio & Video Noise Reducer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

denoiser = InstaAudioDenoiser()

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.post("/api/process")
async def process_file(
    file: UploadFile = File(...),
    preset: str = Form("instagram"),
    reduction_level: int = Form(18)
):
    try:
        temp_input = os.path.join(UPLOAD_DIR, file.filename)
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = denoiser.process_file(
            input_path=temp_input,
            output_dir=OUTPUT_DIR,
            preset=preset,
            reduction_level=reduction_level
        )
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/outputs/{filename}")
def serve_output(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

# Static files if any
if os.path.exists(os.path.join(FRONTEND_DIR, "static")):
    app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
