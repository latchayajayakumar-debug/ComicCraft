from typing import List

from pydantic import BaseModel, Field, field_validator


ALLOWED_TONES = {
    "light-hearted",
    "dramatic",
    "poetic",
    "funny",
}

ALLOWED_STYLES = {
    "anime",
    "pixel art",
    "comic book",
    "realistic",
}


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        min_length=5,
        max_length=2000,
    )

    character_name: str = Field(
        min_length=1,
        max_length=80,
    )

    setting: str = Field(
        min_length=1,
        max_length=200,
    )

    tone: str = Field(
        default="light-hearted"
    )

    art_style: str = Field(
        default="comic book"
    )

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, value: str) -> str:
        if value not in ALLOWED_TONES:
            return "light-hearted"

        return value

    @field_validator("art_style")
    @classmethod
    def validate_style(cls, value: str) -> str:
        if value not in ALLOWED_STYLES:
            return "comic book"

        return value


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class OutlineResponse(BaseModel):
    panels: List[PanelOutline] = Field(
        min_length=5,
        max_length=5,
    )


class StoryPanel(BaseModel):
    panel_number: int
    caption: str
    narration: str
    dialogue: str = ""


class StoryResponse(BaseModel):
    panels: List[StoryPanel] = Field(
        min_length=5,
        max_length=5,
    )


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    image_url: str
    caption: str
    narration: str
    dialogue: str = ""


class ComicResponse(BaseModel):
    comic_id: str
    panels: List[ComicPanel]
    pdf_url: str