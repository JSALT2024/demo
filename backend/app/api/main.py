import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
from .routers import videos


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


app.include_router(videos.router, prefix="/videos", tags=["Videos"])
