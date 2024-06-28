import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
import aiofiles
import os


description = """
Backend web service for the Sign LLM project.
"""


app = FastAPI(
    title="SignLLM backend service",
    description=description,
    version=__version__
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def index():
    path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(path) as f:
        return f.read()


# File uploading code
########################
# https://stackoverflow.com/questions/73442335/how-to-upload-a-large-file-%E2%89%A53gb-to-fastapi-backend

CHUNK_SIZE = 1024 * 1024  # adjust the chunk size as desired

@app.post("/upload")
async def upload(file: UploadFile):
    try:
        filepath = os.path.join("storage", os.path.basename(file.filename))
        async with aiofiles.open(filepath, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="There was an error uploading the file"
        )
    finally:
        await file.close()

    return {"message": f"Successfuly uploaded {file.filename}"}
