"""Headless tests for Flappy Bird's pure logic and a Game smoke test.

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/ -q
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame  # noqa: E402

import game as g  # noqa: E402


# ── difficulty scaling ──
def test_speed_increases_with_score_and_caps():
    assert g.pipe_speed_for_score(0) == g.BASE_PIPE_SPEED
    assert g.pipe_speed_for_score(10) == g.BASE_PIPE_SPEED + 40
    assert g.pipe_speed_for_score(1000) == g.BASE_PIPE_SPEED + 100  # capped


def test_gap_shrinks_and_floors():
    assert g.gap_for_score(0) == g.BASE_GAP
    assert g.gap_for_score(10) == g.BASE_GAP - 10
    assert g.gap_for_score(999) == g.MIN_GAP


# ── medals ──
def test_medals():
    assert g.medal_for_score(0) is None
    assert g.medal_for_score(9) is None
    assert g.medal_for_score(10)[0] == "Bronze"
    assert g.medal_for_score(20)[0] == "Silver"
    assert g.medal_for_score(30)[0] == "Gold"
    assert g.medal_for_score(40)[0] == "Platinum"
    assert g.medal_for_score(99)[0] == "Platinum"


# ── persistent high score ──
def test_high_score_roundtrip(tmp_path):
    path = str(tmp_path / "hs.json")
    assert g.load_high_score(path) == 0          # missing file -> 0
    g.save_high_score(17, path)
    assert g.load_high_score(path) == 17


def test_high_score_corrupt_file_is_safe(tmp_path):
    path = tmp_path / "hs.json"
    path.write_text("not json", encoding="utf-8")
    assert g.load_high_score(str(path)) == 0


# ── pipe collision ──
def test_pipe_collision_and_pass():
    pygame.init()
    pipe = g.Pipe(100, 170)
    inside_gap = pygame.Rect(100, (pipe.top + pipe.bottom) // 2, 10, 10)
    in_top = pygame.Rect(100, 5, 10, 10)
    assert pipe.collides(in_top)
    assert not pipe.collides(inside_gap)


# ── full-game smoke test: state machine runs without a display ──
def test_game_state_machine_smoke():
    pygame.init()
    screen = pygame.display.set_mode((g.WIDTH, g.HEIGHT))
    game = g.Game(screen, g.SoundBank())
    assert game.state == "start"

    game.on_flap_input()
    assert game.state == "playing"

    for _ in range(180):  # ~3 seconds at 60fps steps
        game.update(1 / 60)
        game.draw()
    # Bird either scored, is still flying, or died and settled — all valid,
    # but it must never leave the play field.
    assert 0 <= game.bird.y <= g.HEIGHT
    assert game.state in ("playing", "dying", "dead")

    game.cycle_theme()
    assert game.theme[0] == "Blue"
    game.toggle_pause()
    if game.state == "paused":
        game.toggle_pause()
        assert game.state == "playing"
