# 🐦 Flappy Bird — Python Edition

A fully playable Flappy Bird clone built with Python + Pygame. No external assets needed — all graphics are drawn with pygame primitives.

---

## Features

- Smooth bird physics with gravity + flap animation
- Randomly generated pipes every 1.6 seconds
- Scrolling sky gradient + animated clouds
- Animated grass ground
- Score counter with gold flash on point
- High score tracking across rounds
- Start screen + Game Over screen with retry
- Mouse click or keyboard controls

---

## Controls

| Key / Action | Effect |
|---|---|
| `SPACE` or `↑` | Flap / Start / Retry |
| Mouse click | Flap / Start / Retry |

---

## How to Run

### Step 1 — Create virtual environment

```bash
cd /path/to/flappy-bird
python3 -m venv venv
source venv/bin/activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the game

```bash
python3 game.py
```

---

## Project Structure

```
flappy-bird/
├── game.py          ← entire game (bird, pipes, clouds, UI)
├── requirements.txt ← pygame dependency
├── .gitignore
└── README.md
```

---

## Tech Stack

- **Python 3.9+**
- **Pygame 2.6** — rendering, input, game loop
