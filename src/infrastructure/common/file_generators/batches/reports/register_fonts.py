from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.core.config import BASE_DIR

_fonts_registered = False

FONT_NAME_REGULAR = "TimesNewRoman"
FONT_NAME_BOLD = "TimesNewRomanBold"
FONT_NAME_ITALIC = "TimesNewRomanItalic"


def register_fonts() -> None:
    """Регистрирует кириллические шрифты TimesNewRoman для использования в ReportLab."""
    global _fonts_registered

    if _fonts_registered:
        return

    fonts_dir = BASE_DIR / "fonts"
    regular_font_path = fonts_dir / "TimesNewRoman-Regular.ttf"
    bold_font_path = fonts_dir / "TimesNewRoman-Bold.ttf"
    italic_font_path = fonts_dir / "TimesNewRoman-Italic.ttf"

    pdfmetrics.registerFont(TTFont(FONT_NAME_REGULAR, str(regular_font_path)))
    pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, str(bold_font_path)))
    pdfmetrics.registerFont(TTFont(FONT_NAME_ITALIC, str(italic_font_path)))

    _fonts_registered = True
