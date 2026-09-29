from app.models import (
    ComicPanel,
    OutlineResponse,
    StoryResponse,
)


def build_comic_layout(
    outline: OutlineResponse,
    story: StoryResponse,
    image_urls: list[str],
) -> list[ComicPanel]:

    if len(outline.panels) != 5:
        raise ValueError(
            "Comic outline must contain exactly 5 panels."
        )

    if len(story.panels) != 5:
        raise ValueError(
            "Comic story must contain exactly 5 panels."
        )

    if len(image_urls) != 5:
        raise ValueError(
            "Comic must contain exactly 5 images."
        )

    story_by_number = {
        panel.panel_number: panel
        for panel in story.panels
    }

    layout = []

    for index, panel in enumerate(
        outline.panels
    ):

        story_panel = story_by_number.get(
            panel.panel_number
        )

        if story_panel is None:

            raise ValueError(
                f"Missing story data for "
                f"panel {panel.panel_number}."
            )

        layout.append(
            ComicPanel(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                image_prompt=panel.image_prompt,
                image_url=image_urls[index],
                caption=story_panel.caption,
                narration=story_panel.narration,
                dialogue=story_panel.dialogue,
            )
        )

    return layout