from google import genai
from google.genai import types

from app.config import get_settings
from app.models import (
    OutlineResponse,
    PromptRequest,
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


def generate_outline(
    request: PromptRequest,
) -> OutlineResponse:

    settings = get_settings()

    prompt = f"""
Create a coherent five-panel comic outline.

User story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

1. Return exactly five panels.
2. Keep the same main character visually
   consistent across every panel.
3. Create a clear beginning.
4. Develop the story.
5. Include a turning point.
6. End the story properly.
7. Each panel must contain:
   - panel number
   - short title
   - scene description
   - detailed image generation prompt
8. Image prompts should describe:
   - characters
   - environment
   - composition
   - lighting
   - emotion
   - camera/view
   - requested art style
9. Do not put speech bubble text
   inside the generated image.
"""

    response = _client().models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
            response_schema=OutlineResponse,
        ),
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty outline."
        )

    return OutlineResponse.model_validate_json(
        response.text
    )