from google import genai
from google.genai import types

from app.config import get_settings
from app.models import (
    OutlineResponse,
    PromptRequest,
    StoryResponse,
)


def _client() -> genai.Client:

    settings = get_settings()

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_story(
    request: PromptRequest,
    outline: OutlineResponse,
) -> StoryResponse:

    settings = get_settings()

    outline_text = outline.model_dump_json(
        indent=2
    )

    prompt = f"""
Write the complete five-panel comic story
described below.

User preferences:

Story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Panel outline:
{outline_text}

Requirements:

1. Return exactly five story panels.
2. Use the same panel numbers.
3. Keep names consistent.
4. Keep events consistent.
5. Keep the setting consistent.
6. Keep the main character consistent.
7. Match the requested tone.
8. Each panel must contain:
   - caption
   - narration
   - dialogue
9. Captions should be short.
10. Narration should be 1–3 concise sentences.
11. Dialogue should sound natural.
12. Dialogue can be empty when unnecessary.
13. Do not write image-generation instructions.
"""

    response = _client().models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            response_mime_type="application/json",
            response_schema=StoryResponse,
        ),
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty story."
        )

    return StoryResponse.model_validate_json(
        response.text
    )