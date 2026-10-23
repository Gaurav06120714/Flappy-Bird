![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6-2E8B57?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)

# 🐦 Flappy Bird — Python Edition

A fully playable Flappy Bird clone built with Python + Pygame. No external assets needed — all graphics are drawn with pygame primitives.

---

## Features

- Smooth bird physics with gravity, flap and tilt animation
- Randomly generated pipes with collision detection
- Scrolling sky gradient + animated clouds
- Animated grass ground
- Score counter with gold flash on point
- High score tracking across rounds (in-session)
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

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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

## Roadmap (not yet implemented)

- Difficulty scaling — pipes get faster as score increases
- Medal system — Bronze / Silver / Gold based on score
- Sound effects — flap, score, and death sounds

## Known Issues

- On high-refresh-rate displays (120 Hz), the game-over screen can flicker (see issue #1).
