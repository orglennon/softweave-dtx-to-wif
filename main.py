from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wifwork.net",
        "https://wifwork.com",
        "http://localhost:5174",  # for local dev
    ],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/convert")
async def convert_dtx(file: UploadFile):
    if not file.filename.endswith(".dtx"):
        raise HTTPException(status_code=400, detail="File must be a .dtx file")

    with tempfile.TemporaryDirectory() as tmpdir:
        dtx_path = os.path.join(tmpdir, file.filename)
        wif_path = dtx_path.replace(".dtx", ".wif")

        # Write uploaded file to disk
        with open(dtx_path, "wb") as f:
            f.write(await file.read())

        # Run the converter
        result = subprocess.run(
            ["python", "-m", "dtx_to_wif", dtx_path, wif_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        with open(wif_path, "r") as f:
            wif_content = f.read()

    return { "wif": wif_content }