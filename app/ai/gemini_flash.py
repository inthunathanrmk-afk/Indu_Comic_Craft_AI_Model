import os
import json
import asyncio
from typing import List

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_FLASH_MODEL = os.getenv(
    "GEMINI_FLASH_MODEL",
    "gemini-3.8-flash"
)

DEFAULT_PANELS = int(
    os.getenv("DEFAULT_PANELS", "6")
)


# =========================================================
# GEMINI CLIENT
# =========================================================

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from the .env file."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# DATA MODELS
# =========================================================

class ComicPanel(BaseModel):
    title: str
    description: str
    narration: str
    dialogue: str
    image_prompt: str


class ComicStory(BaseModel):
    title: str
    description: str
    character_name: str
    setting: str
    tone: str
    art_style: str
    panels: List[ComicPanel]


# =========================================================
# BUILD PROMPT
# =========================================================

def build_comic_prompt(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    panel_count: int,
) -> str:

    return f"""
You are an expert comic-book writer.

Create a complete comic story.

Story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Create exactly {panel_count} panels.

The story must have:
1. Beginning
2. Development
3. Conflict
4. Climax
5. Resolution

For every panel provide:

- title
- description
- narration
- dialogue
- image_prompt

Keep the character and setting consistent.

The image_prompt should describe the visual scene clearly.

Do not include text, speech bubbles, captions,
logos, or watermarks inside the image prompt.

Return only JSON matching the requested schema.
"""


# =========================================================
# GENERATE COMIC
# =========================================================

async def generate_comic(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> dict:

    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if not story_prompt.strip():
        raise ValueError("Story prompt cannot be empty.")

    if not character_name.strip():
        raise ValueError("Character name cannot be empty.")

    if not setting.strip():
        raise ValueError("Setting cannot be empty.")

    if not tone.strip():
        raise ValueError("Tone cannot be empty.")

    if not art_style.strip():
        raise ValueError("Art style cannot be empty.")


    # -----------------------------------------------------
    # Build prompt
    # -----------------------------------------------------

    prompt = build_comic_prompt(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
        panel_count=DEFAULT_PANELS,
    )


    # -----------------------------------------------------
    # Gemini request with retry
    # -----------------------------------------------------

    response = None

    for attempt in range(3):

        try:

            print(
                f"Sending request to Gemini "
                f"(attempt {attempt + 1}/3)..."
            )

            response = client.models.generate_content(
                model=GEMINI_FLASH_MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ComicStory,
                    "temperature": 0.8,
                },
            )

            # Request succeeded
            break


        except Exception as exc:

            error_text = str(exc)

            print(
                f"Gemini error: {error_text}"
            )

            # Retry temporary server overload
            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            ):

                if attempt < 2:

                    print(
                        "Gemini is temporarily busy. "
                        "Waiting 5 seconds before retry..."
                    )

                    await asyncio.sleep(5)

                else:

                    raise RuntimeError(
                        "Gemini is currently busy. "
                        "Please try again after a few minutes."
                    ) from exc

            else:

                raise


    # -----------------------------------------------------
    # Check response
    # -----------------------------------------------------

    if response is None:

        raise RuntimeError(
            "Gemini did not return a response."
        )


    # -----------------------------------------------------
    # Parse response
    # -----------------------------------------------------

    try:

        if getattr(response, "parsed", None) is not None:

            comic = response.parsed

        else:

            response_text = getattr(
                response,
                "text",
                None
            )

            if not response_text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            try:

                comic = ComicStory.model_validate_json(
                    response_text
                )

            except Exception:

                data = json.loads(
                    response_text
                )

                comic = ComicStory.model_validate(
                    data
                )


    except Exception as exc:

        raise RuntimeError(
            f"Unable to parse Gemini response: {exc}"
        ) from exc


    # -----------------------------------------------------
    # Convert to dictionary
    # -----------------------------------------------------

    comic_data = comic.model_dump()


    # Add image URL placeholder
    for panel in comic_data["panels"]:

        panel["image_url"] = ""


    return comic_data


# =========================================================
# TEST GEMINI CONNECTION
# =========================================================

async def test_gemini_connection():

    try:

        response = client.models.generate_content(
            model=GEMINI_FLASH_MODEL,
            contents="Reply with exactly: Gemini OK"
        )

        print(response.text)

        return True

    except Exception as exc:

        print(
            f"Gemini connection failed: {exc}"
        )

        return False