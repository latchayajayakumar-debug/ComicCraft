import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models import ComicPanel, PromptRequest
from app.services.exporters import save_pdf
from app.ai.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


router = APIRouter()

settings = get_settings()

templates = Jinja2Templates(
    directory=str(settings.templates_dir)
)


def _comic_file(comic_id: str) -> Path:
    return settings.exports_dir / f"comic-{comic_id}.json"


def _save_comic(
    comic_id: str,
    payload: dict,
) -> None:

    path = _comic_file(comic_id)

    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _load_comic(comic_id: str) -> dict:

    path = _comic_file(comic_id)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Comic not found.",
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
        },
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    payload = PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    try:

        result = await _generate_comic(
            payload
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "app_name": settings.app_name,
                "error": str(exc),
                "form": payload.model_dump(),
            },
            status_code=502,
        )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "app_name": settings.app_name,
            "comic": result,
        },
    )


@router.post(
    "/generate-comic/json",
    response_class=JSONResponse,
)
async def generate_json(
    payload: PromptRequest,
):

    try:

        result = await _generate_comic(
            payload
        )

        return JSONResponse(
            content=result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


async def _generate_comic(
    payload: PromptRequest,
) -> dict:

    # STEP 1
    # Generate five-panel outline
    outline = generate_outline(
        payload
    )

    # STEP 2
    # Generate narration and dialogue
    story = generate_story(
        payload,
        outline,
    )

    # STEP 3
    # Generate images
    image_urls = []

    for panel in outline.panels:

        image_url = generate_image(
            panel.image_prompt,
            panel.panel_number,
        )

        image_urls.append(
            image_url
        )

    # STEP 4
    # Create unique comic ID
    comic_id = uuid4().hex

    # STEP 5
    # Build final layout
    layout = build_comic_layout(
        outline,
        story,
        image_urls,
    )

    # STEP 6
    # Generate PDF
    pdf_url = save_pdf(
        layout,
        comic_id,
    )

    result = {
        "comic_id": comic_id,
        "panels": [
            panel.model_dump()
            for panel in layout
        ],
        "pdf_url": pdf_url,
    }

    # Save comic metadata
    _save_comic(
        comic_id,
        result,
    )

    return result


@router.get(
    "/comic/{comic_id}",
    response_class=HTMLResponse,
)
async def comic_preview(
    request: Request,
    comic_id: str,
):

    comic = _load_comic(
        comic_id
    )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "app_name": settings.app_name,
            "comic": comic,
        },
    )


@router.get(
    "/export/{comic_id}"
)
async def export_comic(
    comic_id: str,
):

    comic = _load_comic(
        comic_id
    )

    pdf_url = comic["pdf_url"]

    pdf_path = (
        settings.static_dir.parent
        / pdf_url.lstrip("/")
    )

    if not pdf_path.exists():

        panels = [
            ComicPanel.model_validate(
                panel
            )
            for panel in comic["panels"]
        ]

        save_pdf(
            panels,
            comic_id,
        )

    if not pdf_path.exists():

        raise HTTPException(
            status_code=404,
            detail="PDF file not found.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"comiccraft-{comic_id}.pdf",
    )


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
    comic_id: Optional[str] = None,
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "app_name": settings.app_name,
            "comic_id": comic_id,
        },
    )


@router.get(
    "/test-image",
    response_class=HTMLResponse,
)
async def test_image_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="test_image.html",
        context={
            "app_name": settings.app_name,
        },
    )


@router.post(
    "/test-image",
    response_class=HTMLResponse,
)
async def test_image(
    request: Request,
    prompt: str = Form(...),
):

    try:

        image_url = generate_image(
            prompt,
            0,
        )

        return templates.TemplateResponse(
            request=request,
            name="test_image.html",
            context={
                "app_name": settings.app_name,
                "image_url": image_url,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="test_image.html",
            context={
                "app_name": settings.app_name,
                "error": str(exc),
            },
            status_code=502,
        )


@router.get("/health")
async def health():

    return {
        "status": "ok",
        "app": settings.app_name,
    }