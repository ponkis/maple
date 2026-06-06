import math
import random
import pygame

class Leaf:
    """
    Simulates a falling leaf with custom swaying, spinning, and scaling characteristics.
    """
    __slots__ = ("base", "x", "y", "vy", "sway_amp", "sway_freq",
                 "sway_phase", "angle", "spin", "scale", "screen_height")

    def __init__(self, screen_width, screen_height, leaf_variants):
        self.base = random.choice(leaf_variants)
        self.x = random.uniform(-40, screen_width + 40)
        self.y = random.uniform(-160, -40)
        self.vy = random.uniform(18, 42)
        self.sway_amp = random.uniform(15, 55)
        self.sway_freq = random.uniform(0.4, 1.3)
        self.sway_phase = random.uniform(0, math.tau)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-25, 25)
        self.scale = random.uniform(0.7, 1.25)
        self.screen_height = screen_height

    def update(self, dt):
        self.y += self.vy * dt
        self.angle += self.spin * dt

    def draw(self, surf, t):
        sway = math.sin(t * self.sway_freq + self.sway_phase) * self.sway_amp
        img = pygame.transform.rotozoom(self.base, self.angle, self.scale)
        rect = img.get_rect(center=(int(self.x + sway), int(self.y)))
        surf.blit(img, rect)

    def offscreen(self):
        return self.y > self.screen_height + 120
