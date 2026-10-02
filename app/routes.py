from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.ai.gemini_flash import generate_comic
from app.services.image_generator import generate_all_panel_images
from app.services.exporters import create_comic_pdf


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

router = APIRouter()

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "comic": None,
            "error": None,
        },
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic_story(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    story_prompt = story_prompt.strip()
    character_name = character_name.strip()
    setting = setting.strip()
    tone = tone.strip()
    art_style = art_style.strip()

    if not story_prompt:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "comic": None,
                "error": "Please enter a story prompt.",
            },
            status_code=400,
        )

    if not character_name:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "comic": None,
                "error": "Please enter a character name.",
            },
            status_code=400,
        )

    if not setting:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "comic": None,
                "error": "Please enter a setting.",
            },
            status_code=400,
        )

    if not tone:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "comic": None,
                "error": "Please select a tone.",
            },
            status_code=400,
        )

    if not art_style:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "comic": None,
                "error": "Please select an art style.",
            },
            status_code=400,
        )

    try:
        # Step 1: Generate comic story using Gemini
        comic = await generate_comic(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        # Step 2: Generate illustrations
        image_urls = await generate_all_panel_images(
            comic["panels"]
        )

        # Step 3: Attach illustrations to panels
        for panel, image_url in zip(
            comic["panels"],
            image_urls,
        ):
            panel["image_url"] = image_url

        # Step 4: Create downloadable PDF
        pdf_url = create_comic_pdf(comic)

        comic["pdf_url"] = pdf_url

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "comic": comic,
                "error": None,
            },
        )

    except Exception as exc:
        print(
            f"Comic generation error: {exc}"
        )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "comic": None,
                "error": (
                    "Comic generation failed. "
                    "Please check your Gemini and "
                    "Hugging Face API keys."
                ),
            },
            status_code=500,
        )


@router.post("/api/generate")
async def generate_comic_api(
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    story_prompt = story_prompt.strip()
    character_name = character_name.strip()
    setting = setting.strip()
    tone = tone.strip()
    art_style = art_style.strip()

    if not story_prompt:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Story prompt is required.",
            },
        )

    if not character_name:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Character name is required.",
            },
        )

    if not setting:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Setting is required.",
            },
        )

    if not tone:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Tone is required.",
            },
        )

    if not art_style:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Art style is required.",
            },
        )

    try:
        # Generate comic story
        comic = await generate_comic(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        # Generate illustrations
        image_urls = await generate_all_panel_images(
            comic["panels"]
        )

        # Attach illustrations
        for panel, image_url in zip(
            comic["panels"],
            image_urls,
        ):
            panel["image_url"] = image_url

        # Create PDF
        pdf_url = create_comic_pdf(comic)

        comic["pdf_url"] = pdf_url

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "comic": comic,
            },
        )

    except Exception as exc:
        print(
            f"API generation error: {exc}"
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": (
                    "Unable to generate the comic. "
                    "Please check your API keys."
                ),
            },
        )


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "ComicCraft",
        "service": "FastAPI",
    }