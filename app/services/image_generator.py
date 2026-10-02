import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

IMAGE_MODEL = os.getenv(
    "IMAGE_MODEL",
    "black-forest-labs/FLUX.1-schnell",
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "static" / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _generate_image_sync(
    prompt: str,
    output_path: Path,
) -> str:
    if not HUGGINGFACE_API_KEY:
        raise RuntimeError(
            "HUGGINGFACE_API_KEY is missing from the .env file."
        )

    client = InferenceClient(
        provider="auto",
        api_key=HUGGINGFACE_API_KEY,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=IMAGE_MODEL,
    )

    image.save(output_path)

    return f"/static/generated/{output_path.name}"


async def generate_panel_image(
    image_prompt: str,
    panel_number: int,
) -> str:
    if not image_prompt.strip():
        raise ValueError(
            "Image prompt cannot be empty."
        )

    output_path = OUTPUT_DIR / (
        f"panel_{panel_number}.png"
    )

    enhanced_prompt = f"""
Create a high-quality comic book illustration.

Scene:
{image_prompt}

Requirements:
- Consistent main character appearance
- Clear facial expressions
- Cinematic composition
- Detailed background
- Strong storytelling through visuals
- High-quality digital comic artwork
- No text
- No speech bubbles
- No captions
- No logos
- No watermark
"""

    return await asyncio.to_thread(
        _generate_image_sync,
        enhanced_prompt,
        output_path,
    )


async def generate_all_panel_images(
    panels: list,
) -> list:
    image_urls = []

    for index, panel in enumerate(panels, start=1):
        image_prompt = panel.get(
            "image_prompt",
            "",
        )

        print(
            f"Generating illustration "
            f"for panel {index}..."
        )

        image_url = await generate_panel_image(
            image_prompt=image_prompt,
            panel_number=index,
        )

        image_urls.append(image_url)

        print(
            f"Panel {index} illustration created."
        )

    return image_urls