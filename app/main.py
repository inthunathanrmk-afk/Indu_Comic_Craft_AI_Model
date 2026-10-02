from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


# ---------------------------------------------------------
# Create required directories
# ---------------------------------------------------------

STATIC_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="ComicCraft AI",
    description=(
        "AI-powered comic story creator using "
        "Google Gemini and image generation."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


# ---------------------------------------------------------
# Application routes
# ---------------------------------------------------------

app.include_router(router)


# ---------------------------------------------------------
# Root-level API information
# ---------------------------------------------------------

@app.get("/api")
async def api_info():
    """
    Return basic information about the ComicCraft API.
    """

    return {
        "application": "ComicCraft AI",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-powered comic story creator",
        "endpoints": {
            "home": "/",
            "generate": "/generate",
            "api_generate": "/api/generate",
            "health": "/health",
            "documentation": "/docs",
        },
    }