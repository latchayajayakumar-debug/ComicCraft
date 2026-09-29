import re
from pathlib import Path
from uuid import uuid4

from huggingface_hub import InferenceClient

from app.config import get_settings


def _safe_name(
    value: str,
) -> str:

    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        value,
    )

    value = value.strip("-")

    return value[:60] or "panel"


def _client() -> InferenceClient:

    settings = get_settings()

    if not settings.hf_api_key:

        raise RuntimeError(
            "HF_API_KEY is missing. "
            "Add your Hugging Face token "
            "to your .env file."
        )

    return InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_api_key,
        timeout=180,
    )


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    settings = get_settings()

    enhanced_prompt = (
        f"{prompt}. "
        "Clean comic illustration, "
        "strong visual storytelling, "
        "consistent character appearance, "
        "cinematic composition, "
        "high detail, "
        "professional artwork, "
        "no readable text, "
        "no watermark."
    )

    image = _client().text_to_image(
        prompt=enhanced_prompt,
        negative_prompt=(
            "blurry, distorted face, "
            "extra limbs, bad anatomy, "
            "text, watermark, logo"
        ),
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
        model=settings.hf_image_model,
    )

    filename = (
        f"{panel_number:02d}-"
        f"{_safe_name(prompt)}-"
        f"{uuid4().hex[:8]}.png"
    )

    output: Path = (
        settings.panels_dir / filename
    )

    image.save(output)

    return (
        f"/static/panels/{filename}"
    )