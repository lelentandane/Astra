# Astra

Astra is a local web app for exploring astrology birth charts. You enter the placements from a chart you already have, and Astra draws an interactive wheel, works out the houses, and lists every placement in one place.

It is built with Flask, SQLite and plain JavaScript. There are no accounts, no external services and no API keys. Your charts stay in a database file on your own computer.

## Features so far

- Enter a chart by hand: Sun, Moon, Ascendant, planets and the North Node, each with sign, degree, minute and retrograde.
- Interactive SVG chart wheel drawn from scratch in JavaScript (zodiac band, degree ticks, house numbers, collision-aware planet placement).
- Whole-sign houses calculated automatically from the Ascendant.
- Hover or focus a planet to highlight its row in the placements table, and the other way round.
- A fictional sample chart to explore before entering your own.
- Server-side validation with clear error messages, and a responsive layout that works on phones.
- Automated tests for the astrology maths, form validation and every route.

## Run it

You need Python 3.10 or newer.

```bash
git clone https://github.com/lelentandane/astra.git
cd astra

python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000 in your browser.

## Run the tests

```bash
python -m pytest
```

## Project structure

```
astra/
  __init__.py        App factory
  astro.py           Signs, bodies, longitude and house maths, form validation
  db.py              SQLite connection handling
  repository.py      All SQL queries
  routes.py          Pages and form handling
  schema.sql         Database tables
  templates/         Jinja pages
  static/css/        Stylesheet and design tokens
  static/js/wheel.js SVG chart wheel
tests/               pytest suite
run.py               Start the app
```

## How the wheel works

Every placement is stored as a sign, degree and minute. Astra converts that to an ecliptic longitude (0 to 360), then to an angle on the wheel relative to the Ascendant's sign, which sits at the left edge. Planets that land close together are nudged apart on screen, while a small tick marks each true position.

## Roadmap

- Aspects between planets, drawn inside the wheel
- Interpretation explorer with topic filters
- Journal notes attached to placements
