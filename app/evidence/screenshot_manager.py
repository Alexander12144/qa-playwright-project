from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class ScreenshotManager:

    def __init__(self, execution_folder: Path):
        self.execution_folder = execution_folder

        self.screenshots_folder = (
            execution_folder / "screenshots"
        )

        self.screenshots_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def _add_url_banner(self, filepath: Path, url: str) -> None:
        try:
            image = Image.open(filepath).convert("RGBA")
        except Exception:
            return

        width, height = image.size
        top_bar_height = 52
        outer_margin = 18
        browser_frame = Image.new(
            "RGBA",
            (width + (outer_margin * 2), height + top_bar_height + (outer_margin * 2) + 8),
            (236, 232, 226, 255),
        )

        draw = ImageDraw.Draw(browser_frame)
        draw.rounded_rectangle(
            (outer_margin, outer_margin, width + outer_margin, outer_margin + top_bar_height),
            radius=12,
            fill=(245, 245, 245, 255),
            outline=(210, 210, 210, 255),
            width=1,
        )
        draw.line(
            (outer_margin, outer_margin + top_bar_height, width + outer_margin, outer_margin + top_bar_height),
            fill=(222, 222, 222, 255),
            width=2,
        )

        for index, color in enumerate([(255, 98, 93), (252, 189, 58), (74, 196, 82)]):
            x = outer_margin + 14 + (index * 18)
            draw.ellipse((x, outer_margin + 16, x + 10, outer_margin + 26), fill=color)

        url_text = url[:120] if url else "about:blank"
        url_box = (
            outer_margin + 170,
            outer_margin + 12,
            outer_margin + width - 90,
            outer_margin + top_bar_height - 10,
        )
        draw.rounded_rectangle(url_box, radius=10, fill=(255, 255, 255, 255), outline=(226, 226, 226, 255), width=1)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        draw.text((outer_margin + 182, outer_margin + 15), url_text, font=font, fill=(30, 30, 30, 255))

        browser_frame.paste(image, (outer_margin, outer_margin + top_bar_height + 8), image.split()[-1])
        browser_frame.save(filepath)

    def capture(self, page, sequence: int) -> str:

        filename = f"E{sequence:03d}.png"

        filepath = self.screenshots_folder / filename

        page.screenshot(
            path=str(filepath),
            full_page=False,
        )

        current_url = getattr(page, "url", "") or ""
        if current_url:
            self._add_url_banner(filepath, current_url)
        else:
            self._add_url_banner(filepath, "about:blank")

        return str(
            Path("screenshots") / filename
        )