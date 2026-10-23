"""
Flappy Bird — Python + Pygame
All graphics drawn with pygame primitives (no external assets needed).

v2 improvements:
- Delta-time physics: the game runs at the same speed on 60 Hz and 120 Hz+
  displays, and the game-over screen is rendered once to a cached surface
  (fixes the flicker reported in issue #1).
- Difficulty scaling: pipes speed up and the gap narrows as the score rises.
- Medal system: Bronze / Silver / Gold / Platinum on the game-over screen.
- Sound effects synthesized at startup (no audio files needed), M to mute.
- Pipe colour themes: press C to cycle Green / Blue / Red / Purple (issue #2).
- Persistent high score saved to highscore.json next to this file.
- Pause with P or Esc, death animation, cached fonts, scrolling ground.
"""

import json
import math
import os
import random
import sys
from array import array

import pygame

# ─────────────────────────────────────────────
# Constants (speeds are pixels per SECOND so physics is frame-rate independent)
# ─────────────────────────────────────────────
WIDTH, HEIGHT = 480, 700
GROUND_H = 80
BIRD_X = 100

SKY_TOP = (30, 140, 255)
SKY_BOT = (135, 206, 250)
GROUND_COL = (210, 170, 90)
GRASS_COL = (80, 180, 60)
BIRD_BODY = (255, 220, 0)
BIRD_WING = (255, 170, 0)
BIRD_EYE = (255, 255, 255)
BIRD_PUPIL = (20, 20, 20)
BIRD_BEAK = (255, 140, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
RED = (220, 50, 50)

GRAVITY = 1620.0          # px/s^2   (was 0.45 px/frame @60fps)
FLAP_STRENGTH = -570.0    # px/s     (was -9.5 px/frame)
MAX_FALL = 840.0          # px/s     (was 14 px/frame)
BASE_PIPE_SPEED = 210.0   # px/s     (was 3.5 px/frame)
PIPE_SPACING = 300        # px between pipes (distance-based spawning)
PIPE_W = 70
BASE_GAP = 170
MIN_GAP = 148

PIPE_THEMES = [
    ("Green",  (50, 200, 50),  (30, 140, 30),  (100, 230, 100)),
    ("Blue",   (50, 130, 230), (30, 90, 170),  (110, 180, 250)),
    ("Red",    (225, 70, 60),  (160, 40, 35),  (245, 120, 110)),
    ("Purple", (150, 80, 220), (105, 50, 165), (190, 140, 250)),
]

MEDALS = [  # (minimum score, name, colour)
    (40, "Platinum", (120, 220, 230)),
    (30, "Gold",     (255, 215, 0)),
    (20, "Silver",   (200, 200, 210)),
    (10, "Bronze",   (205, 127, 50)),
]

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")


# ─────────────────────────────────────────────
# Pure game logic (unit-testable without a display)
# ─────────────────────────────────────────────
def pipe_speed_for_score(score):
    """Pipe speed in px/s: +4 per point, capped at +100."""
    return BASE_PIPE_SPEED + min(score * 4, 100)


def gap_for_score(score):
    """Pipe gap in px: shrinks 1 px per point down to MIN_GAP."""
    return max(BASE_GAP - score, MIN_GAP)


def medal_for_score(score):
    """Return (name, colour) of the medal for a score, or None."""
    for minimum, name, colour in MEDALS:
        if score >= minimum:
            return name, colour
    return None


def load_high_score(path=HIGHSCORE_FILE):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return int(json.load(fh)["high_score"])
    except (OSError, ValueError, KeyError, TypeError):
        return 0


def save_high_score(score, path=HIGHSCORE_FILE):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"high_score": int(score)}, fh)
    except OSError:
        pass  # a read-only folder should never crash the game


# ─────────────────────────────────────────────
# Sound: tiny synthesized effects, no audio assets
# ─────────────────────────────────────────────
class SoundBank:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.sounds = {
                "flap":  self._tone(520, 300, 0.07),
                "score": self._tone(880, 1320, 0.12),
                "hit":   self._tone(200, 60, 0.25),
            }
            self.enabled = True
        except pygame.error:
            self.enabled = False  # no audio device: play silently

    @staticmethod
    def _tone(freq_from, freq_to, seconds, volume=0.35):
        rate = 22050
        frames = int(rate * seconds)
        buf = array("h")
        for i in range(frames):
            t = i / rate
            freq = freq_from + (freq_to - freq_from) * (i / frames)
            fade = 1.0 - (i / frames)
            buf.append(int(32767 * volume * fade * math.sin(2 * math.pi * freq * t)))
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def play(self, name, muted=False):
        if self.enabled and not muted and name in self.sounds:
            self.sounds[name].play()


# ─────────────────────────────────────────────
# Bird
# ─────────────────────────────────────────────
class Bird:
    W, H = 42, 32

    def __init__(self):
        self.x = BIRD_X
        self.y = HEIGHT // 2
        self.vel = 0.0
        self.angle = 0.0
        self.flap_timer = 0.0
        self._rot_cache = {}

    def flap(self):
        self.vel = FLAP_STRENGTH
        self.flap_timer = 0.14

    def update(self, dt):
        self.vel = min(self.vel + GRAVITY * dt, MAX_FALL)
        self.y += self.vel * dt
        target = -25 if self.vel < 0 else min(self.vel * 0.08, 70)
        self.angle += (target - self.angle) * min(1.0, 12 * dt)
        if self.flap_timer > 0:
            self.flap_timer -= dt

    def _base_surface(self):
        surf = pygame.Surface((self.W + 10, self.H + 10), pygame.SRCALPHA)
        bx, by = (self.W + 10) // 2, (self.H + 10) // 2
        pygame.draw.ellipse(surf, BIRD_BODY, (bx - 18, by - 13, 36, 26))
        wing_up = self.flap_timer > 0.07
        wing_off = -4 if wing_up else 4
        pygame.draw.ellipse(surf, BIRD_WING, (bx - 8, by + wing_off, 20, 10))
        pygame.draw.ellipse(surf, (255, 240, 180), (bx - 6, by, 18, 12))
        pygame.draw.circle(surf, BIRD_EYE, (bx + 10, by - 5), 6)
        pygame.draw.circle(surf, BIRD_PUPIL, (bx + 12, by - 5), 3)
        pygame.draw.polygon(surf, BIRD_BEAK, [(bx + 17, by - 3), (bx + 26, by), (bx + 17, by + 3)])
        return surf

    def draw(self, surf):
        key = (round(self.angle / 3), self.flap_timer > 0.07)
        if key not in self._rot_cache:
            if len(self._rot_cache) > 90:
                self._rot_cache.clear()
            self._rot_cache[key] = pygame.transform.rotate(self._base_surface(), -self.angle)
        rotated = self._rot_cache[key]
        surf.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))

    def get_rect(self):
        return pygame.Rect(self.x - 16, self.y - 12, 32, 24)


# ─────────────────────────────────────────────
# Pipe
# ─────────────────────────────────────────────
class Pipe:
    W = PIPE_W

    def __init__(self, x, gap):
        self.x = float(x)
        self.gap = gap
        gap_center = random.randint(180, HEIGHT - GROUND_H - 180)
        self.top = gap_center - gap // 2
        self.bottom = gap_center + gap // 2
        self.passed = False

    def update(self, dt, speed):
        self.x -= speed * dt

    def draw(self, surf, theme):
        _, main, dark, shine = theme
        cap_h = 24
        x = int(self.x)
        # Top pipe (cap flush with the pipe body on both sides)
        pygame.draw.rect(surf, main, (x, 0, self.W, self.top))
        pygame.draw.rect(surf, dark, (x - 4, self.top - cap_h, self.W + 8, cap_h), border_radius=4)
        pygame.draw.rect(surf, shine, (x + 6, 0, 10, max(0, self.top - cap_h)))
        # Bottom pipe
        bottom_h = HEIGHT - GROUND_H - self.bottom
        pygame.draw.rect(surf, main, (x, self.bottom, self.W, bottom_h))
        pygame.draw.rect(surf, dark, (x - 4, self.bottom, self.W + 8, cap_h), border_radius=4)
        pygame.draw.rect(surf, shine, (x + 6, self.bottom + cap_h, 10, max(0, bottom_h - cap_h)))

    def off_screen(self):
        return self.x + self.W < 0

    def collides(self, bird_rect):
        top_rect = pygame.Rect(int(self.x), 0, self.W, self.top)
        bot_rect = pygame.Rect(int(self.x), self.bottom, self.W, HEIGHT - GROUND_H - self.bottom)
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect)


# ─────────────────────────────────────────────
# Cloud
# ─────────────────────────────────────────────
class Cloud:
    def __init__(self, x=None):
        self.x = float(x) if x is not None else WIDTH + random.randint(0, 300)
        self.y = random.randint(40, 220)
        self.speed = random.uniform(24, 54)  # px/s
        self.scale = random.uniform(0.7, 1.3)

    def update(self, dt):
        self.x -= self.speed * dt

    def draw(self, surf):
        cx, cy, s = int(self.x), int(self.y), self.scale
        pygame.draw.ellipse(surf, WHITE, (cx - int(40 * s), cy - int(20 * s), int(80 * s), int(40 * s)))
        pygame.draw.ellipse(surf, WHITE, (cx - int(55 * s), cy - int(10 * s), int(50 * s), int(30 * s)))
        pygame.draw.ellipse(surf, WHITE, (cx + int(10 * s), cy - int(10 * s), int(50 * s), int(30 * s)))

    def off_screen(self):
        return self.x < -150


# ─────────────────────────────────────────────
# Drawing helpers
# ─────────────────────────────────────────────
_font_cache = {}


def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont("Arial Rounded MT Bold", size, bold=True)
    return _font_cache[size]


def draw_text(surf, text, size, x, y, color=WHITE, shadow=True, center=True):
    font = get_font(size)
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surf.blit(s, s.get_rect(center=(x + 2, y + 2)) if center else s.get_rect(topleft=(x + 2, y + 2)))
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y)))


def make_background():
    bg = pygame.Surface((WIDTH, HEIGHT - GROUND_H))
    for y in range(HEIGHT - GROUND_H):
        t = y / (HEIGHT - GROUND_H)
        col = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * t) for i in range(3))
        pygame.draw.line(bg, col, (0, y), (WIDTH, y))
    return bg


def draw_ground(surf, offset):
    ground_y = HEIGHT - GROUND_H
    pygame.draw.rect(surf, GROUND_COL, (0, ground_y, WIDTH, GROUND_H))
    pygame.draw.rect(surf, GRASS_COL, (0, ground_y, WIDTH, 16))
    off = int(offset) % 22
    for x in range(-off, WIDTH, 22):
        pygame.draw.polygon(surf, (60, 160, 40), [(x, ground_y), (x + 6, ground_y - 10), (x + 11, ground_y)])


def draw_panel(surf, x, y, w, h, color):
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill(color)
    pygame.draw.rect(panel, (255, 255, 255, 80), (0, 0, w, h), 3, border_radius=16)
    surf.blit(panel, (x, y))


# ─────────────────────────────────────────────
# Game
# ─────────────────────────────────────────────
class Game:
    """States: start | playing | dying | dead | paused (over playing)."""

    def __init__(self, screen, sounds):
        self.screen = screen
        self.sounds = sounds
        self.bg = make_background()
        self.high_score = load_high_score()
        self.muted = False
        self.theme_idx = 0
        self._dead_panel = None
        self.reset()
        self.state = "start"

    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.clouds = [Cloud(random.randint(0, WIDTH)) for _ in range(5)]
        self.score = 0
        self.score_flash = 0.0
        self.ground_offset = 0.0
        self.death_timer = 0.0
        self._dead_panel = None

    @property
    def theme(self):
        return PIPE_THEMES[self.theme_idx]

    def start_run(self):
        self.reset()
        self.state = "playing"
        self.bird.flap()
        self.sounds.play("flap", self.muted)

    def on_flap_input(self):
        if self.state in ("start", "dead"):
            self.start_run()
        elif self.state == "playing":
            self.bird.flap()
            self.sounds.play("flap", self.muted)

    def toggle_pause(self):
        if self.state == "playing":
            self.state = "paused"
        elif self.state == "paused":
            self.state = "playing"

    def cycle_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(PIPE_THEMES)

    def die(self):
        self.state = "dying"
        self.death_timer = 0.0
        self.bird.vel = min(self.bird.vel, -350.0)  # little bounce up, then fall
        self.sounds.play("hit", self.muted)
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    def update(self, dt):
        for c in self.clouds:
            c.update(dt)
        self.clouds = [c for c in self.clouds if not c.off_screen()]
        if len(self.clouds) < 6:
            self.clouds.append(Cloud())

        if self.state == "playing":
            self.ground_offset += pipe_speed_for_score(self.score) * 0.6 * dt
            self.bird.update(dt)

            if not self.pipes or self.pipes[-1].x < WIDTH - PIPE_SPACING:
                self.pipes.append(Pipe(WIDTH + 10, gap_for_score(self.score)))

            speed = pipe_speed_for_score(self.score)
            for p in self.pipes:
                p.update(dt, speed)
                if not p.passed and p.x + p.W < self.bird.x:
                    p.passed = True
                    self.score += 1
                    self.score_flash = 0.33
                    self.sounds.play("score", self.muted)
                if p.collides(self.bird.get_rect()):
                    self.die()
                    break
            self.pipes = [p for p in self.pipes if not p.off_screen()]

            if self.bird.y - 16 <= 0:      # ceiling: clamp, do not kill
                self.bird.y = 16
                self.bird.vel = max(self.bird.vel, 0)
            if self.bird.y + 16 >= HEIGHT - GROUND_H:
                self.bird.y = HEIGHT - GROUND_H - 16
                self.die()

            if self.score_flash > 0:
                self.score_flash -= dt

        elif self.state == "dying":
            self.death_timer += dt
            if self.bird.y + 16 < HEIGHT - GROUND_H:
                self.bird.vel = min(self.bird.vel + GRAVITY * dt, MAX_FALL)
                self.bird.y += self.bird.vel * dt
                self.bird.angle = min(self.bird.angle + 260 * dt, 90)
            if self.death_timer > 0.55:
                self.state = "dead"

    # ── rendering ──
    def draw(self):
        s = self.screen
        s.blit(self.bg, (0, 0))
        for c in self.clouds:
            c.draw(s)
        for p in self.pipes:
            p.draw(s, self.theme)
        draw_ground(s, self.ground_offset)
        self.bird.draw(s)

        if self.state == "playing":
            col = GOLD if self.score_flash > 0 else WHITE
            draw_text(s, str(self.score), 56, WIDTH // 2, 60, color=col)
        elif self.state == "start":
            self._draw_start(s)
        elif self.state == "dead":
            if self._dead_panel is None:
                self._dead_panel = self._render_dead_panel()
            s.blit(self._dead_panel, (0, 0))
        elif self.state == "paused":
            draw_text(s, "PAUSED", 44, WIDTH // 2, HEIGHT // 2, GOLD)
            draw_text(s, "P or Esc to resume", 20, WIDTH // 2, HEIGHT // 2 + 45, WHITE)

    def _draw_start(self, s):
        draw_panel(s, WIDTH // 2 - 170, HEIGHT // 2 - 150, 340, 300, (0, 0, 0, 140))
        draw_text(s, "🐦 FLAPPY BIRD", 36, WIDTH // 2, HEIGHT // 2 - 105, GOLD)
        draw_text(s, "TAP or SPACE to start", 22, WIDTH // 2, HEIGHT // 2 - 45, WHITE)
        draw_text(s, "C — pipe colour theme", 18, WIDTH // 2, HEIGHT // 2 + 5, (200, 200, 200))
        draw_text(s, "P — pause    M — mute", 18, WIDTH // 2, HEIGHT // 2 + 35, (200, 200, 200))
        draw_text(s, f"Theme: {self.theme[0]}", 18, WIDTH // 2, HEIGHT // 2 + 70, (180, 230, 255))
        if self.high_score > 0:
            draw_text(s, f"Best: {self.high_score}", 22, WIDTH // 2, HEIGHT // 2 + 110, GOLD)

    def _render_dead_panel(self):
        """Rendered once and cached — this is the flicker fix for issue #1."""
        panel = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        draw_panel(panel, WIDTH // 2 - 170, HEIGHT // 2 - 170, 340, 340, (0, 0, 0, 160))
        draw_text(panel, "GAME OVER", 38, WIDTH // 2, HEIGHT // 2 - 120, RED)
        medal = medal_for_score(self.score)
        if medal:
            name, colour = medal
            pygame.draw.circle(panel, colour, (WIDTH // 2, HEIGHT // 2 - 62), 17)
            pygame.draw.circle(panel, (120, 120, 120), (WIDTH // 2, HEIGHT // 2 - 62), 17, 3)
            draw_text(panel, f"{name} medal", 20, WIDTH // 2, HEIGHT // 2 - 28, colour)
        draw_text(panel, "Score", 22, WIDTH // 2, HEIGHT // 2 + 8, (180, 180, 180))
        draw_text(panel, str(self.score), 52, WIDTH // 2, HEIGHT // 2 + 52, WHITE)
        draw_text(panel, f"Best: {self.high_score}", 24, WIDTH // 2, HEIGHT // 2 + 100, GOLD)
        draw_text(panel, "TAP or SPACE to retry", 20, WIDTH // 2, HEIGHT // 2 + 140, (200, 200, 200))
        return panel


def main():
    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=1)
    except TypeError:  # older pygame without vsync kwarg
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    game = Game(screen, SoundBank())

    while True:
        dt = min(clock.tick(240) / 1000.0, 0.033)  # delta seconds, clamped
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    game.on_flap_input()
                elif event.key == pygame.K_c:
                    game.cycle_theme()
                elif event.key == pygame.K_m:
                    game.muted = not game.muted
                elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                    game.toggle_pause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.on_flap_input()
        if game.state != "paused":
            game.update(dt)
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
