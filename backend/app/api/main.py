import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app import __version__


description = """
Backend web service for the Sign LLM project.
"""


app = FastAPI(
    title="SignLLM backend service",
    description=description,
    version=__version__
)


@app.get("/", response_class=HTMLResponse)
def index():
    path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(path) as f:
        return f.read()
