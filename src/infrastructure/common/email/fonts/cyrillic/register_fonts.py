from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_fonts_registered = False


def register_fonts() -> None:
    """Регистрирует кириллические шрифты TimesNewRoman для использования в ReportLab."""
    global _fonts_registered

    if _fonts_registered:
        return

    fonts_dir = Path(__file__).parent
    regular_font_path = fonts_dir / "TimesNewRoman-Regular.ttf"
    bold_font_path = fonts_dir / "TimesNewRoman-Bold.ttf"

    pdfmetrics.registerFont(TTFont("TimesNewRoman", str(regular_font_path)))
    pdfmetrics.registerFont(TTFont("TimesNewRomanBold", str(bold_font_path)))

    _fonts_registered = True
