"""
Flappy Bird — Python + Pygame
All graphics drawn with pygame primitives (no external assets needed).
"""

import pygame
import random
import sys

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
WIDTH, HEIGHT = 480, 700
FPS = 60

# Colors
SKY_TOP    = (30,  140, 255)
SKY_BOT    = (135, 206, 250)
GROUND_COL = (210, 170,  90)
GRASS_COL  = (80,  180,  60)
PIPE_COL   = (50,  200,  50)
PIPE_DARK  = (30,  140,  30)
BIRD_BODY  = (255, 220,   0)
BIRD_WING  = (255, 170,   0)
BIRD_EYE   = (255, 255, 255)
BIRD_PUPIL = (20,   20,  20)
BIRD_BEAK  = (255, 140,   0)
WHITE      = (255, 255, 255)
BLACK      = (0,     0,   0)
GOLD       = (255, 215,   0)
RED        = (220,  50,  50)
DARK_OVERLAY = (0, 0, 0, 160)

GRAVITY       = 0.45
FLAP_STRENGTH = -9.5
PIPE_SPEED    = 3.5
PIPE_GAP      = 170
PIPE_INTERVAL = 1600   # ms
GROUND_H      = 80
BIRD_X        = 100


# ─────────────────────────────────────────────
# Bird
# ─────────────────────────────────────────────
class Bird:
    W, H = 42, 32

    def __init__(self):
        self.x = BIRD_X
        self.y = HEIGHT // 2
        self.vel = 0
        self.angle = 0
        self.alive = True
        self.flap_frame = 0

    def flap(self):
        self.vel = FLAP_STRENGTH
        self.flap_frame = 8

    def update(self):
        self.vel += GRAVITY
        self.vel = min(self.vel, 14)
        self.y += self.vel
        # Angle: tilt up on flap, down on fall
        target = -25 if self.vel < 0 else min(self.vel * 4, 70)
        self.angle += (target - self.angle) * 0.18
        if self.flap_frame > 0:
            self.flap_frame -= 1

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        angle_rad = -self.angle
        import math
        cos_a = math.cos(math.radians(angle_rad))
        sin_a = math.sin(math.radians(angle_rad))

        # Draw on temp surface then rotate
        bird_surf = pygame.Surface((self.W + 10, self.H + 10), pygame.SRCALPHA)
        bx, by = (self.W + 10) // 2, (self.H + 10) // 2

        # Body
        pygame.draw.ellipse(bird_surf, BIRD_BODY, (bx - 18, by - 13, 36, 26))

        # Wing (flapping)
        wing_offset = 4 if self.flap_frame > 4 else -4
        pygame.draw.ellipse(bird_surf, BIRD_WING, (bx - 8, by + wing_offset, 20, 10))

        # Belly
        pygame.draw.ellipse(bird_surf, (255, 240, 180), (bx - 6, by, 18, 12))

        # Eye
        pygame.draw.circle(bird_surf, BIRD_EYE, (bx + 10, by - 5), 6)
        pygame.draw.circle(bird_surf, BIRD_PUPIL, (bx + 12, by - 5), 3)

        # Beak
        pygame.draw.polygon(bird_surf, BIRD_BEAK, [
            (bx + 17, by - 3), (bx + 26, by), (bx + 17, by + 3)
        ])

        rotated = pygame.transform.rotate(bird_surf, -self.angle)
        rect = rotated.get_rect(center=(cx, cy))
        surf.blit(rotated, rect)

    def get_rect(self):
        return pygame.Rect(self.x - 16, self.y - 12, 32, 24)


# ─────────────────────────────────────────────
# Pipe
# ─────────────────────────────────────────────
class Pipe:
    W = 70

    def __init__(self, x):
        self.x = x
        gap_center = random.randint(180, HEIGHT - GROUND_H - 180)
        self.top    = gap_center - PIPE_GAP // 2
        self.bottom = gap_center + PIPE_GAP // 2
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, surf):
        cap_h = 24
        # Top pipe
        pygame.draw.rect(surf, PIPE_COL,  (self.x, 0, self.W, self.top))
        pygame.draw.rect(surf, PIPE_DARK, (self.x, self.top - cap_h, self.W + 8, cap_h), border_radius=4)
        # Shine
        pygame.draw.rect(surf, (100, 230, 100), (self.x + 6, 0, 10, self.top - cap_h))

        # Bottom pipe
        pygame.draw.rect(surf, PIPE_COL,  (self.x, self.bottom, self.W, HEIGHT))
        pygame.draw.rect(surf, PIPE_DARK, (self.x - 8, self.bottom, self.W + 8, cap_h), border_radius=4)
        pygame.draw.rect(surf, (100, 230, 100), (self.x + 6, self.bottom + cap_h, 10, HEIGHT))

    def off_screen(self):
        return self.x + self.W < 0

    def collides(self, bird_rect):
        top_rect = pygame.Rect(self.x, 0, self.W, self.top)
        bot_rect = pygame.Rect(self.x, self.bottom, self.W, HEIGHT)
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect)


# ─────────────────────────────────────────────
# Cloud
# ─────────────────────────────────────────────
class Cloud:
    def __init__(self, x=None):
        self.x = x if x else WIDTH + random.randint(0, 300)
        self.y = random.randint(40, 220)
        self.speed = random.uniform(0.4, 0.9)
        self.scale = random.uniform(0.7, 1.3)

    def update(self):
        self.x -= self.speed

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        s = self.scale
        pygame.draw.ellipse(surf, WHITE, (cx - int(40*s), cy - int(20*s), int(80*s), int(40*s)))
        pygame.draw.ellipse(surf, WHITE, (cx - int(55*s), cy - int(10*s), int(50*s), int(30*s)))
        pygame.draw.ellipse(surf, WHITE, (cx + int(10*s), cy - int(10*s), int(50*s), int(30*s)))

    def off_screen(self):
        return self.x < -150


# ─────────────────────────────────────────────
# Draw sky gradient
# ─────────────────────────────────────────────
def draw_background(surf):
    for y in range(HEIGHT - GROUND_H):
        t = y / (HEIGHT - GROUND_H)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))


def draw_ground(surf):
    ground_y = HEIGHT - GROUND_H
    pygame.draw.rect(surf, GROUND_COL, (0, ground_y, WIDTH, GROUND_H))
    pygame.draw.rect(surf, GRASS_COL, (0, ground_y, WIDTH, 16))
    # Grass tufts
    for x in range(0, WIDTH, 22):
        pygame.draw.polygon(surf, (60, 160, 40), [
            (x, ground_y), (x + 6, ground_y - 10), (x + 11, ground_y)
        ])


# ─────────────────────────────────────────────
# Text helpers
# ─────────────────────────────────────────────
def draw_text(surf, text, size, x, y, color=WHITE, shadow=True, center=True):
    font = pygame.font.SysFont("Arial Rounded MT Bold", size, bold=True)
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        sr = s.get_rect(center=(x + 2, y + 2)) if center else s.get_rect(topleft=(x + 2, y + 2))
        surf.blit(s, sr)
    img = font.render(text, True, color)
    r = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
    surf.blit(img, r)


def draw_panel(surf, x, y, w, h, color=(255, 255, 255, 180)):
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill(color)
    pygame.draw.rect(panel, (255, 255, 255, 80), (0, 0, w, h), 3, border_radius=16)
    surf.blit(panel, (x, y))


# ─────────────────────────────────────────────
# Main Game
# ─────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption("Flappy Bird")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # States: "start" | "playing" | "dead"
    state = "start"

    bird = Bird()
    pipes = []
    clouds = [Cloud(random.randint(0, WIDTH)) for _ in range(5)]
    score = 0
    high_score = 0
    last_pipe = pygame.time.get_ticks() - PIPE_INTERVAL
    ground_x = 0

    # Score flash
    score_flash = 0

    bg = pygame.Surface((WIDTH, HEIGHT - GROUND_H))
    draw_background(bg)

    while True:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if state == "start":
                        state = "playing"
                        bird.flap()
                    elif state == "playing":
                        bird.flap()
                    elif state == "dead":
                        # Restart
                        bird = Bird()
                        pipes = []
                        clouds = [Cloud(random.randint(0, WIDTH)) for _ in range(5)]
                        score = 0
                        last_pipe = now - PIPE_INTERVAL
                        state = "playing"
                        bird.flap()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "start":
                    state = "playing"
                    bird.flap()
                elif state == "playing":
                    bird.flap()
                elif state == "dead":
                    bird = Bird()
                    pipes = []
                    clouds = [Cloud(random.randint(0, WIDTH)) for _ in range(5)]
                    score = 0
                    last_pipe = now - PIPE_INTERVAL
                    state = "playing"
                    bird.flap()

        # ── Update ──
        # Clouds always move
        for c in clouds:
            c.update()
        clouds = [c for c in clouds if not c.off_screen()]
        if len(clouds) < 6:
            clouds.append(Cloud())

        ground_x = (ground_x - PIPE_SPEED * 0.6) % (-WIDTH)

        if state == "playing":
            bird.update()

            # Spawn pipes
            if now - last_pipe > PIPE_INTERVAL:
                pipes.append(Pipe(WIDTH + 10))
                last_pipe = now

            for p in pipes:
                p.update()

                # Score
                if not p.passed and p.x + p.W < bird.x:
                    p.passed = True
                    score += 1
                    score_flash = 20
                    if score > high_score:
                        high_score = score

                # Collision with pipes
                if p.collides(bird.get_rect()):
                    bird.alive = False
                    state = "dead"

            pipes = [p for p in pipes if not p.off_screen()]

            # Ground / ceiling collision
            if bird.y + 16 >= HEIGHT - GROUND_H or bird.y - 16 <= 0:
                bird.alive = False
                state = "dead"

        # ── Draw ──
        screen.blit(bg, (0, 0))

        for c in clouds:
            c.draw(screen)

        for p in pipes:
            p.draw(screen)

        draw_ground(screen)
        bird.draw(screen)

        # ── Score HUD ──
        if state == "playing":
            col = GOLD if score_flash > 0 else WHITE
            if score_flash > 0:
                score_flash -= 1
            draw_text(screen, str(score), 56, WIDTH // 2, 60, color=col)

        # ── Start Screen ──
        if state == "start":
            draw_panel(screen, WIDTH//2 - 160, HEIGHT//2 - 130, 320, 260, (0, 0, 0, 140))
            draw_text(screen, "🐦 FLAPPY BIRD", 36, WIDTH//2, HEIGHT//2 - 90, GOLD)
            draw_text(screen, "TAP  or  SPACE", 24, WIDTH//2, HEIGHT//2 - 20, WHITE)
            draw_text(screen, "to start", 20, WIDTH//2, HEIGHT//2 + 20, (200, 200, 200))
            if high_score > 0:
                draw_text(screen, f"Best: {high_score}", 22, WIDTH//2, HEIGHT//2 + 70, GOLD)
            # Animated bird hint arrow
            arrow_y = HEIGHT//2 + 100 + int(6 * pygame.math.Vector2(1, 0).rotate(now / 5).y)
            draw_text(screen, "▼", 28, WIDTH//2, arrow_y, (180, 230, 255))

        # ── Dead Screen ──
        if state == "dead":
            draw_panel(screen, WIDTH//2 - 160, HEIGHT//2 - 150, 320, 300, (0, 0, 0, 160))
            draw_text(screen, "GAME OVER", 38, WIDTH//2, HEIGHT//2 - 100, RED)
            draw_text(screen, f"Score", 22, WIDTH//2, HEIGHT//2 - 40, (180, 180, 180))
            draw_text(screen, str(score), 52, WIDTH//2, HEIGHT//2 + 10, WHITE)
            draw_text(screen, f"Best: {high_score}", 24, WIDTH//2, HEIGHT//2 + 65, GOLD)
            draw_text(screen, "TAP or SPACE to retry", 20, WIDTH//2, HEIGHT//2 + 115, (200, 200, 200))

        pygame.display.flip()


if __name__ == "__main__":
    main()
