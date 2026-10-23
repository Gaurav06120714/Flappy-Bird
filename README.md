![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6-2E8B57?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)

# 🐦 Flappy Bird — Python Edition

A fully playable Flappy Bird clone built with Python + Pygame. No external assets needed — all graphics are drawn with pygame primitives and all sound effects are synthesized in code.

---

## Features

- Smooth bird physics with gravity, flap and tilt animation
- **Frame-rate independent gameplay** — delta-time physics, identical speed on 60 Hz and 120 Hz+ displays
- **Difficulty scaling** — pipes get faster and the gap narrows as your score rises
- **Medal system** — Bronze (10), Silver (20), Gold (30), Platinum (40) on the game-over screen
- **Sound effects** — synthesized flap, score and hit sounds, no audio files needed
- **Pipe colour themes** — Green, Blue, Red, Purple (issue #2)
- **Persistent high score** — saved to `highscore.json` between sessions
- Randomly generated pipes with collision detection
- Scrolling sky gradient, animated clouds and scrolling ground
- Death animation, pause, and a flicker-free game-over screen (issue #1 fixed)
- Score counter with gold flash on point
- Start screen + Game Over screen with retry

---

## Controls

| Key / Action | Effect |
|---|---|
| `SPACE` or `↑` | Flap / Start / Retry |
| Mouse click | Flap / Start / Retry |
| `C` | Cycle pipe colour theme |
| `P` or `Esc` | Pause / resume |
| `M` | Mute / unmute sound |

---

## How to Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 game.py
```

---

## Tests

Headless logic + smoke tests (no display needed):

```bash
pip install pygame pytest
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/ -q
```

CI runs the same suite on every push and pull request.

---

## Project Structure

```
flappy-bird/
├── game.py               ← entire game (bird, pipes, clouds, sound, UI)
├── tests/
│   └── test_game_logic.py
├── .github/workflows/
│   └── tests.yml         ← CI: pytest on push / PR
├── requirements.txt      ← pygame dependency
├── .gitignore
└── README.md
```

---

## Tech Stack

- **Python 3.9+**
- **Pygame 2.6** — rendering, input, game loop, synthesized audio
