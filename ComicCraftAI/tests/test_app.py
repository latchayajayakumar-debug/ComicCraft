from fastapi.testclient import TestClient

from app.main import app
from app.models import (
    OutlineResponse,
    StoryResponse,
)
from app.services.layout_builder import (
    build_comic_layout,
)


client = TestClient(app)


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_docs():

    response = client.get(
        "/docs"
    )

    assert response.status_code == 200


def test_layout_builder():

    outline = OutlineResponse.model_validate(
        {
            "panels": [
                {
                    "panel_number": i,
                    "title": f"T{i}",
                    "scene_description": f"S{i}",
                    "image_prompt": f"I{i}",
                }
                for i in range(1, 6)
            ]
        }
    )

    story = StoryResponse.model_validate(
        {
            "panels": [
                {
                    "panel_number": i,
                    "caption": f"C{i}",
                    "narration": f"N{i}",
                    "dialogue": f"D{i}",
                }
                for i in range(1, 6)
            ]
        }
    )

    layout = build_comic_layout(
        outline,
        story,
        [
            f"/static/panels/{i}.png"
            for i in range(1, 6)
        ],
    )

    assert len(layout) == 5

    assert layout[0].title == "T1"

    assert layout[4].dialogue == "D5"