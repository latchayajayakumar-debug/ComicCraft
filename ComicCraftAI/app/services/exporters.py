from pathlib import Path
from typing import List

from fpdf import FPDF
from PIL import Image

from app.config import get_settings
from app.models import ComicPanel


class ComicPDF(FPDF):

    def header(self):

        self.set_font(
            "Helvetica",
            "B",
            16,
        )

        self.cell(
            0,
            10,
            "ComicCraft",
            ln=True,
            align="C",
        )

        self.ln(2)


def _local_image(
    url: str,
) -> Path:

    settings = get_settings()

    parsed = urlparse(url)

    path = parsed.path.lstrip("/")

    return (
        settings.static_dir.parent
        / path
    )


def _pdf_text(value: str) -> str:

    """
    FPDF's built-in Helvetica font uses a
    limited encoding. Replace common Unicode
    punctuation so generated Gemini text does
    not break PDF export.
    """

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        "…": "...",
        "•": "*",
        "→": "->",
    }

    for old, new in replacements.items():
        value = value.replace(
            old,
            new,
        )

    return value.encode(
        "latin-1",
        "replace",
    ).decode(
        "latin-1"
    )


def save_pdf(
    panels: list[ComicPanel],
    comic_id: str = None,
) -> str:

    settings = get_settings()

    comic_id = (
        comic_id
        or uuid4().hex
    )

    filename = (
        f"comic-{comic_id}.pdf"
    )

    output = (
        settings.exports_dir
        / filename
    )

    pdf = ComicPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in panels:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            14,
        )

        pdf.multi_cell(
            0,
            8,
            _pdf_text(
                f"Panel {panel.panel_number}: "
                f"{panel.title}"
            ),
        )

        pdf.ln(2)

        image_path = _local_image(
            panel.image_url
        )

        if image_path.exists():

            with Image.open(
                image_path
            ) as img:

                width, height = img.size

            max_width = 180
            max_height = 105

            ratio = min(
                max_width / width,
                max_height / height,
            )

            pdf.image(
                str(image_path),
                w=width * ratio,
                h=height * ratio,
            )

            pdf.ln(4)

        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                panel.scene_description
            ),
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                f"Caption: {panel.caption}"
            ),
        )

        pdf.ln(1)

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                f"Narration: {panel.narration}"
            ),
        )

        if panel.dialogue:

            pdf.ln(1)

            pdf.multi_cell(
                0,
                6,
                _pdf_text(
                    f"Dialogue: "
                    f"{panel.dialogue}"
                ),
            )

    pdf.output(
        str(output)
    )

    return (
        f"/static/exports/{filename}"
    )