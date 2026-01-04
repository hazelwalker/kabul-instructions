"""
KABUL Card Game - Unified Print Generator
==========================================

Generates BOTH print-ready editions from a single content source:
1. Full Edition (4 cards) - with decorative back sides
2. Compact Edition (2 cards) - rules on front AND back

Change the content once → both PDFs update automatically.

Output files:
- kabul_cards_4card_edition.pdf  (4 rule cards + decorative backs)
- kabul_cards_2card_edition.pdf  (2 cards, rules on both sides)

Usage:
    python kabul_cards_unified.py

Print settings:
    - Duplex: Long edge flip (Lange Kante spiegeln)
    - Scale: 100% (do not fit to page)
    - Cut along crop marks
"""

from reportlab.lib.pagesizes import mm, A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import os
import sys


# =============================================================================
# CONFIGURATION - Edit these values to customize output
# =============================================================================

# Language selection: "de" (German) or "en" (English)
LANGUAGE = "de"

OUTPUT_DIR = "./cards"  # Current directory (change as needed)

# Card dimensions (Poker standard: 63x88mm)
CARD_WIDTH = 63 * mm
CARD_HEIGHT = 88 * mm

# Print settings
BLEED = 3 * mm              # Beschnittzugabe
CROP_LENGTH = 5 * mm        # Length of crop marks
CROP_OFFSET = 3 * mm        # Distance from card edge
CROP_LINE_WIDTH = 0.25      # Crop mark thickness

# Layout
CARD_SPACING = 8 * mm       # Space between cards
MARGIN = 3.5 * mm           # Content margin inside card

# Derived constants (don't edit)
CARD_WIDTH_BLEED = CARD_WIDTH + 2 * BLEED
CARD_HEIGHT_BLEED = CARD_HEIGHT + 2 * BLEED
PAGE_WIDTH, PAGE_HEIGHT = A4


# =============================================================================
# COLORS - Customize the color scheme here
# =============================================================================

class Colors:
    """
    Color palette for KABUL cards.

    To customize:
        - Change hex values (e.g., "#C41E3A" → "#0066CC" for blue accent)
        - Keep bg white for best print results
    """
    # Main colors
    bg = HexColor("#FFFFFF")          # Card background (keep white)
    text = HexColor("#1A1A1A")        # Main text color
    accent = HexColor("#C41E3A")      # Accent color (Japanese red)
    heading = HexColor("#2D2D2D")     # Heading text color

    # Card symbols
    red = HexColor("#C41E3A")         # ♥ ♦ color
    black = HexColor("#1A1A1A")       # ♠ ♣ color

    # Background decoration
    shape_light = HexColor("#F7F7F7")   # Back wave (lighter)
    shape_medium = HexColor("#EEEEEE")  # Front wave (darker)
    shape_accent = HexColor("#FEF5F6")  # Accent circle (light pink)

    # Back side colors (4-card edition)
    back_base = HexColor("#C41E3A")      # Back background
    back_wave1 = HexColor("#A01830")     # Back wave 1
    back_wave2 = HexColor("#8A1428")     # Back wave 2
    back_circle = HexColor("#D42A4A")    # Back accent circle

    # Print marks
    crop_mark = HexColor("#000000")


# =============================================================================
# TYPOGRAPHY - Customize fonts and sizes here
# =============================================================================

class Fonts:
    """
    Typography settings.

    Uses Arial (available on Windows) with DejaVuSans as Linux fallback.
    """
    title = "CardFont-Bold"
    heading = "CardFont-Bold"
    body = "CardFont"

    # Font sizes (in points)
    title_size = 13       # "KABUL" title
    subtitle_size = 7.5   # Card subtitle
    heading_size = 7      # Section headings
    body_size = 6.2       # Body text
    number_size = 6       # Card number (1/4, 2/4, etc.)


# =============================================================================
# CARD CONTENT - Bilingual (German / English)
# =============================================================================
#
# Edit the content below to update BOTH PDF editions automatically.
# Change LANGUAGE at the top to switch between "de" and "en".
#
# =============================================================================

CONTENT = {
    # =========================================================================
    # GERMAN CONTENT
    # =========================================================================
    "de": {
        "card_1_values": [
            ("Joker", "-1 Punkt", None, False),
            ("Ass", "1 Punkt", None, False),
            ("2–6", "Kartenwert", None, False),
            ("7, 8", "Kartenwert", "Eigene ansehen", False),
            ("9, 10", "Kartenwert", "Fremde ansehen", False),
            ("Bube, Dame", "10 Punkte", "Tauschen", False),
            ("König ♠♣", "10 Punkte", "2× Ansehen & Tauschen?", False),
            ("König ♥♦", "0 Punkte", None, True),
        ],
        "card_1": {
            "title": "Kartenwerte & Aktionen",
            "type": "values_table",
            "footer_sections": [
                {"heading": "Ziel", "content": "Niedrigste Gesamtpunktzahl"},
                {"heading": "Ende", "content": "Erster Spieler > 100 Punkte"},
            ]
        },
        "card_2": {
            "title": "Spielablauf",
            "type": "sections",
            "sections": [
                {
                    "heading": "Setup",
                    "content": [
                        "4 Karten verdeckt im Quadrat",
                        "Untere 2 Karten einmal ansehen",
                        "Erste Karte vom Stapel aufdecken"
                    ]
                },
                {
                    "heading": "Spielzug",
                    "content": [
                        "1. Karte ziehen von Stapel o. Ablage",
                        "2. Wählen: Ablegen, Ersetzen",
                        "   oder Kartenaktion ausführen"
                    ]
                },
                {
                    "heading": "Abwerfen",
                    "content": [
                        "Gleiche Karte wie auf der Ablage?",
                        "→ Eigene/fremde Karte draufschmeißen!",
                        "Schnellster gewinnt · 1× pro Abwerfen"
                    ]
                },
                {
                    "heading": "Kabul",
                    "content": [
                        "Bei ≤4 Punkten: Kabul rufen",
                        "→ Löst letzte Runde aus"
                    ]
                }
            ]
        },
        "card_3": {
            "title": "Detailregeln",
            "type": "sections",
            "sections": [
                {
                    "heading": "Abwerfen-Details",
                    "content": [
                        "Auch fremde Karten abwerfbar",
                        "Eigene Karte als Ersatz geben",
                        "Schnellster gewinnt",
                        "Berührt Ablage = gültig",
                        "Zählt nicht als Spielzug"
                    ]
                },
                {
                    "heading": "Karte ersetzen",
                    "content": [
                        "Sofort umdrehen & zeigen",
                        "Nicht erst anschauen!"
                    ]
                },
                {
                    "heading": "Sonderfälle",
                    "content": [
                        "Stapel leer → Ablage mischen",
                        "Keine Karten mehr → Kabul (Pflicht)"
                    ]
                }
            ]
        },
        "card_4": {
            "title": "Strafen & Regeln",
            "type": "sections",
            "sections": [
                {
                    "heading": "Strafen (+1 Karte)",
                    "content": [
                        "Setup: Karten 2× angesehen",
                        "Falsches Abwerfen"
                    ]
                },
                {
                    "heading": "Kabul-Strafe",
                    "content": [
                        "Nicht niedrigste Anzahl oder >4 Punkte?",
                        "→ Kartenzahl verdoppelt",
                        "oder",
                        "→ Nächste Runde: 5 Karten"
                    ]
                },
                {
                    "heading": "Wichtig",
                    "content": [
                        "Kabul erst ab ≤4 Punkte rufbar",
                        "Am Ende: Bestätigung nötig",
                        "Nach Abwerfen: Eigener Zug möglich",
                        "Kartenaktion = Ablegen + Aktion"
                    ]
                },
                {
                    "heading": "Gleichstand",
                    "content": ["Der, der Kabul gerufen hat gewinnt"]
                }
            ]
        },
        "back_title": "KABUL",
        "back_subtitle": "Kartenspiel",
        "title_card_title": "KABUL",
        "title_card_subtitle": "Spielregeln",
        "github_url": "https://github.com/hazelwalker/kabul-instructions",
        "game_description": [
            "KABUL ist ein schnelles Kartenspiel für 2-6 Spieler,",
            "inspiriert von Cabo, Skyjo oder Golf. Ziel ist es, die",
            "niedrigste Punktzahl zu erreichen – aber Vorsicht:",
            "Du kennst nicht alle deine Karten!",
            "",
            "Merke dir deine Karten, tausche clever und rufe",
            "»Kabul!«, wenn du glaubst zu gewinnen.",
            "",
            "Spieldauer: ca. 15-20 Minuten",
        ],
        "about_title": "Über das Spiel",
        "page_info": {
            "4card_front": "Vorderseiten",
            "4card_back": "Rückseiten",
            "4card_edition": "Regelkarten",
            "2card_front": "Vorderseiten: Kartenwerte | Detailregeln",
            "2card_back": "Rückseiten: Spielablauf | Strafen",
            "2card_edition": "Kompakt",
            "title_front": "Vorderseite",
            "title_back": "Rückseite",
            "duplex_hint": "↻ Duplex: Lange Kante spiegeln",
        }
    },

    # =========================================================================
    # ENGLISH CONTENT
    # =========================================================================
    "en": {
        "card_1_values": [
            ("Joker", "-1 Point", None, False),
            ("Ace", "1 Point", None, False),
            ("2–6", "Face Value", None, False),
            ("7, 8", "Face Value", "View own card", False),
            ("9, 10", "Face Value", "View other's card", False),
            ("Jack, Queen", "10 Points", "Swap cards", False),
            ("King ♠♣", "10 Points", "2× View & Swap?", False),
            ("King ♥♦", "0 Points", None, True),
        ],
        "card_1": {
            "title": "Card Values & Actions",
            "type": "values_table",
            "footer_sections": [
                {"heading": "Goal", "content": "Lowest total score"},
                {"heading": "End", "content": "First player > 100 points"},
            ]
        },
        "card_2": {
            "title": "Gameplay",
            "type": "sections",
            "sections": [
                {
                    "heading": "Setup",
                    "content": [
                        "4 cards face-down in a square",
                        "Look at bottom 2 cards once",
                        "Flip first card from draw pile"
                    ]
                },
                {
                    "heading": "Turn",
                    "content": [
                        "1. Draw card from pile or discard",
                        "2. Choose: Discard, Replace",
                        "   or use card action"
                    ]
                },
                {
                    "heading": "Smash",
                    "content": [
                        "Same card as on discard pile?",
                        "→ Smash your/other's card on top!",
                        "Fastest wins · 1× per smash"
                    ]
                },
                {
                    "heading": "Kabul",
                    "content": [
                        "At ≤4 points: Call Kabul",
                        "→ Triggers final round"
                    ]
                }
            ]
        },
        "card_3": {
            "title": "Detailed Rules",
            "type": "sections",
            "sections": [
                {
                    "heading": "Smash Details",
                    "content": [
                        "Can smash other players' cards too",
                        "Give own card as replacement",
                        "Fastest player wins",
                        "Touching discard = valid",
                        "Does not count as turn"
                    ]
                },
                {
                    "heading": "Replace Card",
                    "content": [
                        "Flip immediately & show",
                        "Don't peek first!"
                    ]
                },
                {
                    "heading": "Special Cases",
                    "content": [
                        "Draw pile empty → Shuffle discard",
                        "No cards left → Kabul (mandatory)"
                    ]
                }
            ]
        },
        "card_4": {
            "title": "Penalties & Rules",
            "type": "sections",
            "sections": [
                {
                    "heading": "Penalties (+1 Card)",
                    "content": [
                        "Setup: Looked at cards twice",
                        "Wrong smash"
                    ]
                },
                {
                    "heading": "Kabul Penalty",
                    "content": [
                        "Not lowest or >4 points?",
                        "→ Double your card count",
                        "or",
                        "→ Next round: 5 cards"
                    ]
                },
                {
                    "heading": "Important",
                    "content": [
                        "Kabul only callable at ≤4 points",
                        "End: Confirmation required",
                        "After smash: Own turn possible",
                        "Card action = Discard + Action"
                    ]
                },
                {
                    "heading": "Tie",
                    "content": ["Kabul caller wins"]
                }
            ]
        },
        "back_title": "KABUL",
        "back_subtitle": "Card Game",
        "title_card_title": "KABUL",
        "title_card_subtitle": "Game Rules",
        "github_url": "https://github.com/hazelwalker/kabul-instructions",
        "game_description": [
            "KABUL is a fast-paced card game for 2-6 players,",
            "inspired by Cabo, Skyjo and Golf. The goal is to achieve",
            "the lowest score – but beware:",
            "You don't know all your cards!",
            "",
            "Memorize your cards, swap cleverly, and call",
            "»Kabul!« when you think you'll win.",
            "",
            "Duration: approx. 15-20 minutes",
        ],
        "about_title": "About the Game",
        "page_info": {
            "4card_front": "Front Sides",
            "4card_back": "Back Sides",
            "4card_edition": "Rule Cards",
            "2card_front": "Front: Card Values | Detailed Rules",
            "2card_back": "Back: Gameplay | Penalties",
            "2card_edition": "Compact",
            "title_front": "Front Side",
            "title_back": "Back Side",
            "duplex_hint": "↻ Duplex: Long Edge Flip",
        }
    }
}


# =============================================================================
# ACTIVE CONTENT (loaded based on LANGUAGE setting)
# =============================================================================

def get_content():
    """Get content for the selected language."""
    lang = CONTENT[LANGUAGE]

    # Build CARD_1 with values
    card_1 = lang["card_1"].copy()
    card_1["values"] = lang["card_1_values"]

    return {
        "CARD_1": card_1,
        "CARD_2": lang["card_2"],
        "CARD_3": lang["card_3"],
        "CARD_4": lang["card_4"],
        "BACK_TITLE": lang["back_title"],
        "BACK_SUBTITLE": lang["back_subtitle"],
        "TITLE_CARD_TITLE": lang["title_card_title"],
        "TITLE_CARD_SUBTITLE": lang["title_card_subtitle"],
        "GITHUB_URL": lang["github_url"],
        "GAME_DESCRIPTION": lang["game_description"],
        "ABOUT_TITLE": lang["about_title"],
        "PAGE_INFO": lang["page_info"],
    }


# =============================================================================
# FONT REGISTRATION - Cross-platform (Windows + Linux)
# =============================================================================

def register_fonts():
    """
    Register fonts for PDF generation.

    Tries Windows fonts first (Arial), then Linux fonts (DejaVuSans).
    Falls back to Helvetica if nothing else works.
    """
    fonts_registered = False

    # Windows font paths
    windows_fonts = {
        'CardFont': 'C:/Windows/Fonts/arial.ttf',
        'CardFont-Bold': 'C:/Windows/Fonts/arialbd.ttf',
    }

    # Linux font paths
    linux_fonts = {
        'CardFont': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'CardFont-Bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    }

    # Try Windows fonts first
    if sys.platform == 'win32':
        font_paths = windows_fonts
    else:
        font_paths = linux_fonts

    for name, path in font_paths.items():
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                fonts_registered = True
            except Exception as e:
                print(f"Warning: Could not register font {name}: {e}")

    # Fallback: try the other platform's fonts
    if not fonts_registered:
        fallback = linux_fonts if sys.platform == 'win32' else windows_fonts
        for name, path in fallback.items():
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(name, path))
                    fonts_registered = True
                except:
                    pass

    # Ultimate fallback: use Helvetica (built into ReportLab)
    if not fonts_registered:
        print("Warning: Using Helvetica as fallback font")
        Fonts.title = "Helvetica-Bold"
        Fonts.heading = "Helvetica-Bold"
        Fonts.body = "Helvetica"


# =============================================================================
# DRAWING FUNCTIONS - Crop Marks
# =============================================================================

def draw_crop_marks(c, x, y, width, height):
    """
    Draw crop marks at all four corners of a card.

    Args:
        c: Canvas object
        x, y: Bottom-left corner of card (including bleed)
        width, height: Card dimensions (including bleed)
    """
    c.saveState()
    c.setStrokeColor(Colors.crop_mark)
    c.setLineWidth(CROP_LINE_WIDTH)

    # Calculate cut line positions (inside bleed)
    cut_left = x + BLEED
    cut_right = x + width - BLEED
    cut_bottom = y + BLEED
    cut_top = y + height - BLEED

    # Top-left corner
    c.line(cut_left - CROP_OFFSET - CROP_LENGTH, cut_top,
           cut_left - CROP_OFFSET, cut_top)
    c.line(cut_left, cut_top + CROP_OFFSET,
           cut_left, cut_top + CROP_OFFSET + CROP_LENGTH)

    # Top-right corner
    c.line(cut_right + CROP_OFFSET, cut_top,
           cut_right + CROP_OFFSET + CROP_LENGTH, cut_top)
    c.line(cut_right, cut_top + CROP_OFFSET,
           cut_right, cut_top + CROP_OFFSET + CROP_LENGTH)

    # Bottom-left corner
    c.line(cut_left - CROP_OFFSET - CROP_LENGTH, cut_bottom,
           cut_left - CROP_OFFSET, cut_bottom)
    c.line(cut_left, cut_bottom - CROP_OFFSET - CROP_LENGTH,
           cut_left, cut_bottom - CROP_OFFSET)

    # Bottom-right corner
    c.line(cut_right + CROP_OFFSET, cut_bottom,
           cut_right + CROP_OFFSET + CROP_LENGTH, cut_bottom)
    c.line(cut_right, cut_bottom - CROP_OFFSET - CROP_LENGTH,
           cut_right, cut_bottom - CROP_OFFSET)

    c.restoreState()


# =============================================================================
# DRAWING FUNCTIONS - Background
# =============================================================================

def draw_front_background(c, x, y):
    """
    Draw the front side background with wave design and accent circle.

    Layers (back to front):
        1. White base
        2. Back wave (light gray)
        3. Front wave (darker gray)
        4. Accent circle (pink, on top of waves)
        5. Red accent bar at top

    Args:
        x, y: Cut line position (not bleed)
    """
    # Drawing area with bleed
    draw_x = x - BLEED
    draw_y = y - BLEED
    draw_width = CARD_WIDTH + 2 * BLEED
    draw_height = CARD_HEIGHT + 2 * BLEED

    # Layer 1: White base
    c.setFillColor(Colors.bg)
    c.rect(draw_x, draw_y, draw_width, draw_height, fill=1, stroke=0)

    # Layer 2: Back wave (lighter, higher)
    c.saveState()
    path_back = c.beginPath()
    path_back.moveTo(draw_x, y + 25*mm)
    path_back.curveTo(
        x + 20*mm, y + 35*mm,
        x + 35*mm, y + 50*mm,
        draw_x + draw_width, y + 60*mm
    )
    path_back.lineTo(draw_x + draw_width, draw_y)
    path_back.lineTo(draw_x, draw_y)
    path_back.close()
    c.setFillColor(Colors.shape_light)
    c.drawPath(path_back, fill=1, stroke=0)
    c.restoreState()

    # Layer 3: Front wave (darker, lower)
    c.saveState()
    path_front = c.beginPath()
    path_front.moveTo(draw_x, y + 15*mm)
    path_front.curveTo(
        x + 25*mm, y + 22*mm,
        x + 40*mm, y + 35*mm,
        draw_x + draw_width, y + 45*mm
    )
    path_front.lineTo(draw_x + draw_width, draw_y)
    path_front.lineTo(draw_x, draw_y)
    path_front.close()
    c.setFillColor(Colors.shape_medium)
    c.drawPath(path_front, fill=1, stroke=0)
    c.restoreState()

    # Layer 4: Accent circle (on top of waves)
    c.saveState()
    c.setFillColor(Colors.shape_accent)
    c.circle(x + 50*mm, y + 20*mm, 12*mm, fill=1, stroke=0)
    c.restoreState()

    # Layer 5: Red accent bar at top
    c.setFillColor(Colors.accent)
    c.rect(draw_x, y + CARD_HEIGHT - 3.5*mm, draw_width, 3.5*mm + BLEED, fill=1, stroke=0)


def draw_back_background(c, x, y, content):
    """
    Draw the decorative back side (4-card edition only).

    Red-themed design with waves and KABUL branding.
    """
    draw_x = x - BLEED
    draw_y = y - BLEED
    draw_width = CARD_WIDTH + 2 * BLEED
    draw_height = CARD_HEIGHT + 2 * BLEED

    # Base color
    c.setFillColor(Colors.back_base)
    c.rect(draw_x, draw_y, draw_width, draw_height, fill=1, stroke=0)

    # Wave 1 (darker)
    c.saveState()
    path = c.beginPath()
    path.moveTo(draw_x, y + 30*mm)
    path.curveTo(x + 20*mm, y + 40*mm, x + 40*mm, y + 55*mm, draw_x + draw_width, y + 65*mm)
    path.lineTo(draw_x + draw_width, draw_y)
    path.lineTo(draw_x, draw_y)
    path.close()
    c.setFillColor(Colors.back_wave1)
    c.drawPath(path, fill=1, stroke=0)
    c.restoreState()

    # Wave 2 (darkest)
    c.saveState()
    path2 = c.beginPath()
    path2.moveTo(draw_x, y + 18*mm)
    path2.curveTo(x + 25*mm, y + 25*mm, x + 45*mm, y + 38*mm, draw_x + draw_width, y + 48*mm)
    path2.lineTo(draw_x + draw_width, draw_y)
    path2.lineTo(draw_x, draw_y)
    path2.close()
    c.setFillColor(Colors.back_wave2)
    c.drawPath(path2, fill=1, stroke=0)
    c.restoreState()

    # Accent circle
    c.saveState()
    c.setFillColor(Colors.back_circle)
    c.circle(x + 50*mm, y + 22*mm, 10*mm, fill=1, stroke=0)
    c.restoreState()

    # KABUL text
    c.setFillColor(Colors.bg)
    c.setFont(Fonts.title, 18)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT/2 + 5*mm, content["BACK_TITLE"])

    c.setFont(Fonts.body, 8)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT/2 - 5*mm, content["BACK_SUBTITLE"])


def draw_title_card_background(c, x, y, content):
    """
    Draw the title card (same design as back, but with "Spielregeln" subtitle).

    This card can be used as a cover card for the rule set.
    """
    draw_x = x - BLEED
    draw_y = y - BLEED
    draw_width = CARD_WIDTH + 2 * BLEED
    draw_height = CARD_HEIGHT + 2 * BLEED

    # Base color
    c.setFillColor(Colors.back_base)
    c.rect(draw_x, draw_y, draw_width, draw_height, fill=1, stroke=0)

    # Wave 1 (darker)
    c.saveState()
    path = c.beginPath()
    path.moveTo(draw_x, y + 30*mm)
    path.curveTo(x + 20*mm, y + 40*mm, x + 40*mm, y + 55*mm, draw_x + draw_width, y + 65*mm)
    path.lineTo(draw_x + draw_width, draw_y)
    path.lineTo(draw_x, draw_y)
    path.close()
    c.setFillColor(Colors.back_wave1)
    c.drawPath(path, fill=1, stroke=0)
    c.restoreState()

    # Wave 2 (darkest)
    c.saveState()
    path2 = c.beginPath()
    path2.moveTo(draw_x, y + 18*mm)
    path2.curveTo(x + 25*mm, y + 25*mm, x + 45*mm, y + 38*mm, draw_x + draw_width, y + 48*mm)
    path2.lineTo(draw_x + draw_width, draw_y)
    path2.lineTo(draw_x, draw_y)
    path2.close()
    c.setFillColor(Colors.back_wave2)
    c.drawPath(path2, fill=1, stroke=0)
    c.restoreState()

    # Accent circle
    c.saveState()
    c.setFillColor(Colors.back_circle)
    c.circle(x + 50*mm, y + 22*mm, 10*mm, fill=1, stroke=0)
    c.restoreState()

    # KABUL title (larger)
    c.setFillColor(Colors.bg)
    c.setFont(Fonts.title, 20)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT/2 + 8*mm, content["TITLE_CARD_TITLE"])

    # "Spielregeln" subtitle
    c.setFont(Fonts.body, 9)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT/2 - 4*mm, content["TITLE_CARD_SUBTITLE"])


def draw_title_card(c, x, y, content):
    """Draw the title card with clipping and crop marks."""
    c.saveState()
    clip_path = c.beginPath()
    clip_path.rect(x - BLEED, y - BLEED, CARD_WIDTH_BLEED, CARD_HEIGHT_BLEED)
    c.clipPath(clip_path, stroke=0, fill=0)

    draw_title_card_background(c, x, y, content)
    c.restoreState()

    draw_crop_marks(c, x - BLEED, y - BLEED, CARD_WIDTH_BLEED, CARD_HEIGHT_BLEED)


def draw_title_card_back(c, x, y, content):
    """
    Draw the back of the title card with game description and QR code.

    Contains:
    - Short game description
    - QR code linking to GitHub repository
    """
    draw_x = x - BLEED
    draw_y = y - BLEED
    draw_width = CARD_WIDTH + 2 * BLEED
    draw_height = CARD_HEIGHT + 2 * BLEED

    # White background
    c.setFillColor(Colors.bg)
    c.rect(draw_x, draw_y, draw_width, draw_height, fill=1, stroke=0)

    # Red accent bar at top (matching front design)
    c.setFillColor(Colors.accent)
    c.rect(draw_x, y + CARD_HEIGHT - 3.5*mm, draw_width, 3.5*mm + BLEED, fill=1, stroke=0)

    # Title
    c.setFont(Fonts.title, 11)
    c.setFillColor(Colors.text)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT - 12*mm, content["ABOUT_TITLE"])

    # Game description
    c.setFont(Fonts.body, 6)
    c.setFillColor(Colors.text)

    text_y = y + CARD_HEIGHT - 20*mm
    for line in content["GAME_DESCRIPTION"]:
        if line == "":
            text_y -= 2*mm
        else:
            c.drawCentredString(x + CARD_WIDTH/2, text_y, line)
            text_y -= 3.2*mm

    # QR Code
    qr_size = 18 * mm
    qr_code = qr.QrCodeWidget(content["GITHUB_URL"])
    qr_code.barLevel = 'M'
    qr_code.barWidth = qr_size
    qr_code.barHeight = qr_size

    # Create drawing and render QR code
    d = Drawing(qr_size, qr_size)
    d.add(qr_code)

    qr_x = x + (CARD_WIDTH - qr_size) / 2
    qr_y = y + 12*mm
    renderPDF.draw(d, c, qr_x, qr_y)

    # URL label below QR code
    c.setFont(Fonts.body, 4.5)
    c.setFillColor(Colors.heading)
    c.drawCentredString(x + CARD_WIDTH/2, y + 8*mm, "github.com/hazelwalker/kabul-instructions")


def draw_title_card_back_with_marks(c, x, y, content):
    """Draw title card back with clipping and crop marks."""
    c.saveState()
    clip_path = c.beginPath()
    clip_path.rect(x - BLEED, y - BLEED, CARD_WIDTH_BLEED, CARD_HEIGHT_BLEED)
    c.clipPath(clip_path, stroke=0, fill=0)

    draw_title_card_back(c, x, y, content)
    c.restoreState()

    draw_crop_marks(c, x - BLEED, y - BLEED, CARD_WIDTH_BLEED, CARD_HEIGHT_BLEED)


# =============================================================================
# DRAWING FUNCTIONS - Content
# =============================================================================

def draw_title(c, x, y, title, number):
    """Draw card title and number."""
    # Main title
    c.setFont(Fonts.title, Fonts.title_size)
    c.setFillColor(Colors.text)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT - 11*mm, "KABUL")

    # Subtitle
    c.setFont(Fonts.body, Fonts.subtitle_size)
    c.setFillColor(Colors.heading)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT - 16.5*mm, title)

    # Card number (bottom right)
    c.setFont(Fonts.body, Fonts.number_size)
    c.setFillColor(Colors.accent)
    c.drawRightString(x + CARD_WIDTH - MARGIN - 0.5*mm, y + MARGIN + 1*mm, number)


def draw_values_table(c, x, y, card_data):
    """Draw card values with aligned columns (for Card 1)."""
    content_y = y + CARD_HEIGHT - 21*mm

    # Column positions
    col_label = x + MARGIN + 1*mm
    col_equals = x + 24*mm
    col_value = x + 27*mm

    c.setFont(Fonts.body, Fonts.body_size)

    for label, value, action, has_red in card_data["values"]:
        # Handle card symbols with colors
        if "♠♣" in label:
            parts_before = label.split("♠♣")[0]
            c.setFillColor(Colors.text)
            c.drawString(col_label, content_y, parts_before)
            symbol_x = col_label + c.stringWidth(parts_before, Fonts.body, Fonts.body_size)
            c.setFillColor(Colors.black)
            c.drawString(symbol_x, content_y, "♠♣")
        elif "♥♦" in label:
            parts_before = label.split("♥♦")[0]
            c.setFillColor(Colors.text)
            c.drawString(col_label, content_y, parts_before)
            symbol_x = col_label + c.stringWidth(parts_before, Fonts.body, Fonts.body_size)
            c.setFillColor(Colors.red)
            c.drawString(symbol_x, content_y, "♥♦")
        else:
            c.setFillColor(Colors.text)
            c.drawString(col_label, content_y, label)

        # Aligned "=" and value
        c.setFillColor(Colors.text)
        c.drawString(col_equals, content_y, "=")
        c.drawString(col_value, content_y, value)

        # Action (indented, next line)
        if action:
            content_y -= 2.8*mm
            c.setFillColor(Colors.heading)
            c.drawString(col_value, content_y, f"→ {action}")
            c.setFillColor(Colors.text)

        content_y -= 3.2*mm

    # Footer sections
    content_y -= 1.5*mm
    for footer in card_data["footer_sections"]:
        c.setFont(Fonts.heading, Fonts.heading_size)
        c.setFillColor(Colors.heading)
        c.drawString(col_label, content_y, footer["heading"])

        c.setFont(Fonts.body, Fonts.body_size)
        c.setFillColor(Colors.text)
        heading_width = c.stringWidth(footer["heading"] + "  ", Fonts.heading, Fonts.heading_size)
        c.drawString(col_label + heading_width, content_y, footer["content"])
        content_y -= 3.5*mm


def draw_sections(c, x, y, card_data):
    """Draw content sections with headings (for Cards 2-4)."""
    content_y = y + CARD_HEIGHT - 21*mm

    for section in card_data["sections"]:
        # Section heading (bold)
        c.setFont(Fonts.heading, Fonts.heading_size)
        c.setFillColor(Colors.heading)
        c.drawString(x + MARGIN + 1*mm, content_y, section["heading"])
        content_y -= 3.3*mm

        # Section content
        c.setFont(Fonts.body, Fonts.body_size)
        c.setFillColor(Colors.text)

        for line in section["content"]:
            indent = 0
            if line.startswith("   "):
                indent = 2.5*mm
                line = line.strip()

            # Style arrows in accent color
            if line.startswith("→"):
                c.setFillColor(Colors.accent)
                c.drawString(x + MARGIN + 1*mm + indent, content_y, "→")
                c.setFillColor(Colors.text)
                c.drawString(x + MARGIN + 1*mm + indent + 3*mm, content_y, line[2:])
            else:
                c.drawString(x + MARGIN + 1*mm + indent, content_y, line)

            content_y -= 2.9*mm

        content_y -= 1.2*mm


def draw_card_front(c, x, y, card_data, number):
    """Draw a complete front side card."""
    # Clip to bleed area
    c.saveState()
    clip_path = c.beginPath()
    clip_path.rect(x - BLEED, y - BLEED, CARD_WIDTH_BLEED, CARD_HEIGHT_BLEED)
    c.clipPath(clip_path, stroke=0, fill=0)

    # Background
    draw_front_background(c, x, y)
    c.restoreState()

    # Title
    draw_title(c, x, y, card_data["title"], number)

    # Content
    if card_data["type"] == "values_table":
        draw_values_table(c, x, y, card_data)
    else:
        draw_sections(c, x, y, card_data)

    # Crop marks
    draw_crop_marks(c, x - BLEED, y - BLEED, CARD_WIDTH_BLEED, CARD_HEIGHT_BLEED)


def draw_card_back(c, x, y, content):
    """Draw a decorative back side card (4-card edition)."""
    c.saveState()
    clip_path = c.beginPath()
    clip_path.rect(x - BLEED, y - BLEED, CARD_WIDTH_BLEED, CARD_HEIGHT_BLEED)
    c.clipPath(clip_path, stroke=0, fill=0)

    draw_back_background(c, x, y, content)
    c.restoreState()

    draw_crop_marks(c, x - BLEED, y - BLEED, CARD_WIDTH_BLEED, CARD_HEIGHT_BLEED)


# =============================================================================
# PAGE LAYOUT
# =============================================================================

def draw_page_info(c, page_num, total_pages, description, edition):
    """Draw page information footer."""
    c.setFont(Fonts.body, 7)
    c.setFillColor(HexColor("#999999"))

    info = f"KABUL {edition} | Seite {page_num}/{total_pages} | {description} | 63×88mm"
    c.drawString(15*mm, 10*mm, info)

    if page_num == 2:
        c.drawRightString(PAGE_WIDTH - 15*mm, 10*mm, "↻ Duplex: Lange Kante spiegeln")


def calculate_4card_positions():
    """Calculate positions for 2x2 card layout."""
    total_width = 2 * CARD_WIDTH_BLEED + CARD_SPACING
    total_height = 2 * CARD_HEIGHT_BLEED + CARD_SPACING

    start_x = (PAGE_WIDTH - total_width) / 2 + BLEED
    start_y = (PAGE_HEIGHT - total_height) / 2 + BLEED

    front = [
        (start_x, start_y + CARD_HEIGHT_BLEED + CARD_SPACING),
        (start_x + CARD_WIDTH_BLEED + CARD_SPACING, start_y + CARD_HEIGHT_BLEED + CARD_SPACING),
        (start_x, start_y),
        (start_x + CARD_WIDTH_BLEED + CARD_SPACING, start_y),
    ]

    # Mirrored for duplex
    back = [
        (start_x + CARD_WIDTH_BLEED + CARD_SPACING, start_y + CARD_HEIGHT_BLEED + CARD_SPACING),
        (start_x, start_y + CARD_HEIGHT_BLEED + CARD_SPACING),
        (start_x + CARD_WIDTH_BLEED + CARD_SPACING, start_y),
        (start_x, start_y),
    ]

    return front, back


def calculate_2card_positions():
    """Calculate positions for 2 cards side by side."""
    total_width = 2 * CARD_WIDTH_BLEED + CARD_SPACING
    start_x = (PAGE_WIDTH - total_width) / 2 + BLEED
    start_y = (PAGE_HEIGHT - CARD_HEIGHT_BLEED) / 2 + BLEED

    front = [
        (start_x, start_y),
        (start_x + CARD_WIDTH_BLEED + CARD_SPACING, start_y),
    ]

    # Mirrored for duplex
    back = [
        (start_x + CARD_WIDTH_BLEED + CARD_SPACING, start_y),
        (start_x, start_y),
    ]

    return front, back


# =============================================================================
# PDF GENERATION - 4-Card Edition
# =============================================================================

def generate_4card_edition(output_path):
    """
    Generate the 4-card edition with decorative back sides.

    Page 1: Front sides (Cards 1-4)
    Page 2: Back sides (mirrored for duplex)
    """
    content = get_content()
    c = canvas.Canvas(output_path, pagesize=A4)
    front_pos, back_pos = calculate_4card_positions()

    cards = [
        (content["CARD_1"], "1/4"),
        (content["CARD_2"], "2/4"),
        (content["CARD_3"], "3/4"),
        (content["CARD_4"], "4/4"),
    ]

    # Page 1: Front sides
    for i, (card_data, number) in enumerate(cards):
        draw_card_front(c, front_pos[i][0], front_pos[i][1], card_data, number)

    page_info = content["PAGE_INFO"]
    c.setFont(Fonts.body, 7)
    c.setFillColor(HexColor("#999999"))
    info = f"KABUL {page_info['4card_edition']} | Page 1/2 | {page_info['4card_front']} | 63×88mm"
    c.drawString(15*mm, 10*mm, info)
    c.showPage()

    # Page 2: Back sides (decorative)
    for i in range(4):
        draw_card_back(c, back_pos[i][0], back_pos[i][1], content)

    c.setFont(Fonts.body, 7)
    c.setFillColor(HexColor("#999999"))
    info = f"KABUL {page_info['4card_edition']} | Page 2/2 | {page_info['4card_back']} | 63×88mm"
    c.drawString(15*mm, 10*mm, info)
    c.drawRightString(PAGE_WIDTH - 15*mm, 10*mm, page_info['duplex_hint'])
    c.save()

    print(f"✓ 4-Card Edition ({LANGUAGE.upper()}): {output_path}")


# =============================================================================
# PDF GENERATION - 2-Card Compact Edition
# =============================================================================

def generate_2card_edition(output_path):
    """
    Generate the compact 2-card edition with rules on both sides.

    Card 1: Kartenwerte (front) / Spielablauf (back)
    Card 2: Detailregeln (front) / Strafen (back)

    Page 1: Front sides
    Page 2: Back sides (mirrored for duplex)
    """
    content = get_content()
    c = canvas.Canvas(output_path, pagesize=A4)
    front_pos, back_pos = calculate_2card_positions()

    # Page 1: Front sides
    draw_card_front(c, front_pos[0][0], front_pos[0][1], content["CARD_1"], "1a")
    draw_card_front(c, front_pos[1][0], front_pos[1][1], content["CARD_3"], "2a")

    page_info = content["PAGE_INFO"]
    c.setFont(Fonts.body, 7)
    c.setFillColor(HexColor("#999999"))
    info = f"KABUL {page_info['2card_edition']} | Page 1/2 | {page_info['2card_front']} | 63×88mm"
    c.drawString(15*mm, 10*mm, info)
    c.showPage()

    # Page 2: Back sides (mirrored)
    draw_card_front(c, back_pos[0][0], back_pos[0][1], content["CARD_2"], "1b")
    draw_card_front(c, back_pos[1][0], back_pos[1][1], content["CARD_4"], "2b")

    c.setFont(Fonts.body, 7)
    c.setFillColor(HexColor("#999999"))
    info = f"KABUL {page_info['2card_edition']} | Page 2/2 | {page_info['2card_back']} | 63×88mm"
    c.drawString(15*mm, 10*mm, info)
    c.drawRightString(PAGE_WIDTH - 15*mm, 10*mm, page_info['duplex_hint'])
    c.save()

    print(f"✓ 2-Card Edition ({LANGUAGE.upper()}): {output_path}")


# =============================================================================
# PDF GENERATION - Title Card
# =============================================================================

def generate_title_card(output_path):
    """
    Generate title card PDF with front and back side.

    Front: Red design with "KABUL - Spielregeln"
    Back: Game description + QR code to GitHub repo

    Optimized for duplex printing (long-edge flip).
    """
    content = get_content()
    c = canvas.Canvas(output_path, pagesize=A4)

    # Center single card on page
    x = (PAGE_WIDTH - CARD_WIDTH) / 2
    y = (PAGE_HEIGHT - CARD_HEIGHT) / 2

    page_info = content["PAGE_INFO"]

    # Page 1: Front (title)
    draw_title_card(c, x, y, content)

    c.setFont(Fonts.body, 7)
    c.setFillColor(HexColor("#999999"))
    c.drawString(15*mm, 10*mm, f"KABUL Title Card | Page 1/2 | {page_info['title_front']} | 63×88mm")
    c.showPage()

    # Page 2: Back (description + QR)
    draw_title_card_back_with_marks(c, x, y, content)

    c.setFont(Fonts.body, 7)
    c.setFillColor(HexColor("#999999"))
    c.drawString(15*mm, 10*mm, f"KABUL Title Card | Page 2/2 | {page_info['title_back']} | 63×88mm")
    c.drawRightString(PAGE_WIDTH - 15*mm, 10*mm, page_info['duplex_hint'])

    c.save()

    print(f"✓ Title Card ({LANGUAGE.upper()}): {output_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Generate all KABUL card editions."""
    print("=" * 50)
    print(f"KABUL Card Generator (Language: {LANGUAGE.upper()})")
    print("=" * 50)

    register_fonts()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate all editions with language suffix
    lang_suffix = f"_{LANGUAGE}"
    generate_4card_edition(f"{OUTPUT_DIR}/kabul_cards_4card{lang_suffix}.pdf")
    generate_2card_edition(f"{OUTPUT_DIR}/kabul_cards_2card{lang_suffix}.pdf")
    generate_title_card(f"{OUTPUT_DIR}/kabul_cards_title{lang_suffix}.pdf")

    print()
    if LANGUAGE == "de":
        print("Druckeinstellungen:")
        print("  • Duplex: Lange Kante spiegeln")
        print("  • Skalierung: 100% (nicht skalieren)")
        print("  • Entlang Schnittmarken schneiden")
    else:
        print("Print settings:")
        print("  • Duplex: Long edge flip")
        print("  • Scale: 100% (do not fit to page)")
        print("  • Cut along crop marks")
    print()
    print(f"Output: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()