from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dtx_to_wif.pattern_reader import read_pattern_data
from dtx_to_wif.wif_writer import write_wif
import io

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

    data = (await file.read()).decode("utf-8")
    try:
        pattern = read_pattern_data(data, ".dtx", file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    buf = io.StringIO()
    write_wif(buf, pattern)
    return {"wif": buf.getvalue()}