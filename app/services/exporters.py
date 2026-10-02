import re
from pathlib import Path

from fpdf import FPDF


BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "static" / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(title: str) -> str:
    filename = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        title.strip(),
    )

    filename = filename.strip("_")

    if not filename:
        filename = "comic"

    return filename[:80]


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
            "ComicCraft AI",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        self.ln(3)

    def footer(self):
        self.set_y(-15)

        self.set_font(
            "Helvetica",
            "",
            8,
        )

        self.cell(
            0,
            10,
            f"Page {self.page_no()}",
            align="C",
        )


def create_comic_pdf(comic: dict) -> str:
    title = comic.get(
        "title",
        "ComicCraft Comic",
    )

    filename = (
        f"{safe_filename(title)}.pdf"
    )

    output_path = OUTPUT_DIR / filename

    pdf = ComicPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    pdf.add_page()

    # Comic title
    pdf.set_font(
        "Helvetica",
        "B",
        24,
    )

    pdf.multi_cell(
        0,
        12,
        title,
        align="C",
    )

    pdf.ln(5)

    # Comic description
    description = comic.get(
        "description",
        "",
    )

    if description:
        pdf.set_font(
            "Helvetica",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            description,
        )

        pdf.ln(5)

    # Comic information
    pdf.set_font(
        "Helvetica",
        "B",
        11,
    )

    pdf.cell(
        0,
        7,
        f"Character: {comic.get('character_name', '')}",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.cell(
        0,
        7,
        f"Setting: {comic.get('setting', '')}",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.cell(
        0,
        7,
        f"Tone: {comic.get('tone', '')}",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.cell(
        0,
        7,
        f"Art Style: {comic.get('art_style', '')}",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(8)

    # Panels
    panels = comic.get(
        "panels",
        [],
    )

    for index, panel in enumerate(
        panels,
        start=1,
    ):
        pdf.set_font(
            "Helvetica",
            "B",
            16,
        )

        pdf.cell(
            0,
            10,
            f"Panel {index}: {panel.get('title', '')}",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        # Illustration
        image_url = panel.get(
            "image_url",
            "",
        )

        if image_url.startswith(
            "/static/"
        ):
            image_path = (
                BASE_DIR / image_url.lstrip("/")
            )

            if image_path.exists():
                try:
                    pdf.image(
                        str(image_path),
                        w=170,
                    )

                    pdf.ln(5)

                except Exception as exc:
                    print(
                        f"PDF image error: {exc}"
                    )

        # Description
        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.cell(
            0,
            7,
            "Scene:",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            panel.get(
                "description",
                "",
            ),
        )

        pdf.ln(2)

        # Narration
        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.cell(
            0,
            7,
            "Narration:",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            panel.get(
                "narration",
                "",
            ),
        )

        pdf.ln(2)

        # Dialogue
        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.cell(
            0,
            7,
            "Dialogue:",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            panel.get(
                "dialogue",
                "",
            ),
        )

        pdf.ln(8)

    pdf.output(str(output_path))

    return f"/static/generated/{filename}"