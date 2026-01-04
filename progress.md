# Progress: KABUL Kartenspiel – Regelkarten-Generator

## Projektbeschreibung

Druckfertige Regelkarten für das Kartenspiel **KABUL** (ähnlich Cabo/Golf). 
Das Python-Skript generiert professionelle PDF-Dateien mit:
- Japanisch-minimalistischem Design (Wave + Circle)
- Schnittmarken und 3mm Beschnittzugabe
- Duplex-optimiertem Layout für beidseitigen Druck
- Farbigen Kartensymbolen (♥♦ rot, ♠♣ schwarz)

**Zielformat:** Poker-Standardkarten (63×88mm)

---

## Current Status

✅ **Abgeschlossen**
- Unified Generator (`main.py`) erzeugt beide Editionen aus einer Content-Quelle
- 4-Karten-Edition mit dekorativen Rückseiten
- 2-Karten-Kompakt-Edition (Regeln auf Vorder- UND Rückseite)
- Wave-Design mit Akzentkreis (inspiriert von Quartett-Karten)
- Tabellarische Ausrichtung der Kartenwerte (= aligned)
- "Smash" → "Abwerfen" ersetzt
- Windows-Kompatibilität (Arial als Font)

---

## Output Files

| Datei | Beschreibung |
|-------|--------------|
| `main.py` | **Haupt-Skript** – generiert alle PDFs |
| `kabul_cards_4card_edition.pdf` | 4 Regelkarten + KABUL-Rückseiten |
| `kabul_cards_2card_edition.pdf` | 2 Kompaktkarten (beidseitig bedruckt) |
| `kabul_cards_title.pdf` | Titelkarte (Vorderseite: Logo, Rückseite: QR-Code + Beschreibung) |

---

## Technical Decisions

### Design
- **Stil:** Tokyo-Minimal mit Wave-Hintergrund + rosa Akzentkreis
- **Farbschema:** Japanisches Rot (#C41E3A) als Akzent, warme Grautöne für Wellen
- **Typografie:** Arial (Windows) / DejaVuSans (Linux) mit Helvetica-Fallback
- **Schriftgrößen:** Titel 13pt, Überschriften 7pt, Body 6.2pt

### Druck
- **Bleed:** 3mm Beschnittzugabe
- **Crop Marks:** 5mm Länge, 3mm Abstand vom Kartenrand
- **Duplex:** Lange Kante spiegeln (Positionen auf Seite 2 horizontal gespiegelt)

### Code-Architektur
- Single Source of Truth: `CARD_1` bis `CARD_4` Dictionaries
- Modulare Zeichenfunktionen: `draw_front_background()`, `draw_sections()`, etc.
- Separate Generator-Funktionen für jede Edition
- Cross-Platform Font-Registrierung (Windows + Linux)

---

## Aktuelle Kartenwerte (Stand: 2025-01-04)

| Karte | Punkte | Aktion |
|-------|--------|--------|
| Joker | -1 | – |
| Ass | 1 | – |
| 2–6 | Kartenwert | – |
| 7, 8 | Kartenwert | Eigene ansehen |
| 9, 10 | Kartenwert | Fremde ansehen |
| Bube, Dame | 10 | Tauschen |
| König ♠♣ | 10 | 2× Ansehen & Tauschen? |
| König ♥♦ | 0 | – |

---

## Anpassungen

### Sprache ändern
```python
# In main.py, Zeile ~35
LANGUAGE = "de"  # Deutsch
LANGUAGE = "en"  # English
```
Output-Dateien werden automatisch mit Sprachsuffix benannt:
- `kabul_cards_4card_de.pdf` / `kabul_cards_4card_en.pdf`

### Content ändern
```python
# In main.py, Zeile ~100-200
CARD_2 = {
    "title": "Spielablauf",
    "sections": [
        {"heading": "Setup", "content": ["...", "..."]},
        # Änderungen hier → beide PDFs aktualisieren sich
    ]
}
```

### Farben ändern
```python
class Colors:
    accent = HexColor("#C41E3A")      # Akzentfarbe
    shape_light = HexColor("#F7F7F7") # Hintere Welle
    shape_accent = HexColor("#FEF5F6") # Akzentkreis
```

### Hintergrund-Elemente
```python
# Wellen-Kurve anpassen (in draw_front_background):
path_back.curveTo(
    x + 20*mm, y + 35*mm,   # Control Point 1
    x + 35*mm, y + 50*mm,   # Control Point 2
    x + CARD_WIDTH, y + 60*mm  # Endpunkt
)

# Akzentkreis Position/Größe:
c.circle(x + 50*mm, y + 20*mm, 12*mm, ...)  # x, y, radius
```

---

## Druckanleitung

1. PDF öffnen → Drucken
2. **Beidseitig:** "Lange Kante spiegeln" wählen
3. **Skalierung:** 100% (nicht anpassen!)
4. Entlang Schnittmarken ausschneiden
5. Optional: Laminieren für Haltbarkeit

---

## Offene Punkte / Ideen

- [ ] Alternative Farbschemata (z.B. Blau-Variante)
- [ ] Englische Version der Regeln
- [ ] QR-Code mit Link zu ausführlichen Regeln
- [ ] Einzelkarten-Export für professionellen Druck

---

## Session History

| Datum | Änderungen |
|-------|------------|
| 2025-01-04 | Initial: Design-Analyse des Originals, Verbesserungsvorschläge |
| 2025-01-04 | 3 Stil-Varianten erstellt (Zen, Wabi-Sabi, Tokyo) |
| 2025-01-04 | Tokyo + grafische Hintergründe (Wave, Circles, Diagonal, Geometric) |
| 2025-01-04 | Wave + Circle kombiniert, tabellarische Ausrichtung, farbige Symbole |
| 2025-01-04 | Print-Ready Version mit Schnittmarken und Bleed |
| 2025-01-04 | Kompakt 2-Karten-Version erstellt |
| 2025-01-04 | Unified Script: beide Editionen aus einer Content-Quelle |
| 2025-01-04 | "Smash" → "Abwerfen" ersetzt |
| 2025-01-04 | Content aus händisch korrigierter PDF übernommen |
| 2025-01-04 | Windows-Kompatibilität (Arial-Fonts) hinzugefügt |
| 2025-01-04 | Titelkarte hinzugefügt (rotes Design mit "Spielregeln") |
| 2025-01-04 | Titelkarten-Rückseite: QR-Code + Spielbeschreibung |
| 2025-01-04 | Zweisprachige Unterstützung (DE/EN) mit LANGUAGE-Variable |