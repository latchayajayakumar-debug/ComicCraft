from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router


settings = get_settings()


app = FastAPI(
    title="ComicCraft API",
    description=(
        "AI Comic Story Creator using Gemini "
        "and Hugging Face image generation"
    ),
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(settings.static_dir)
    ),
    name="static",
)


app.include_router(router)


@app.get(
    "/favicon.ico",
    include_in_schema=False,
)
async def favicon():
    return {}