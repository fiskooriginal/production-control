from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_NAME_REGULAR = "TimesNewRoman"
FONT_NAME_BOLD = "TimesNewRomanBold"

_fonts_registered = False


def register_fonts() -> None:
    """Регистрирует шрифты TimesNewRoman для использования в ReportLab."""
    global _fonts_registered

    if _fonts_registered:
        return

    fonts_dir = Path(__file__).parent
    regular_font_path = fonts_dir / "TimesNewRoman-Regular.ttf"
    bold_font_path = fonts_dir / "TimesNewRoman-Bold.ttf"

    pdfmetrics.registerFont(TTFont(FONT_NAME_REGULAR, str(regular_font_path)))
    pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, str(bold_font_path)))

    _fonts_registered = True
