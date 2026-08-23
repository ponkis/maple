import math
import random

import pygame


class Leaf:
    """
    Simulate a falling leaf with resolution-aware motion and drawing.
    """

    __slots__ = (
        "base",
        "x",
        "y",
        "vy",
        "sway_amp",
        "sway_freq",
        "sway_phase",
        "angle",
        "spin",
        "scale",
        "screen_height",
        "offscreen_margin",
    )

    def __init__(self, screen_width, screen_height, leaf_variants, scene_scale=1.0):
        motion_scale = max(float(scene_scale), 0.01)
        horizontal_margin = 40 * motion_scale

        self.base = random.choice(leaf_variants)
        self.x = random.uniform(-horizontal_margin, screen_width + horizontal_margin)
        self.y = random.uniform(-160 * motion_scale, -40 * motion_scale)
        self.vy = random.uniform(18, 42) * motion_scale
        self.sway_amp = random.uniform(15, 55) * motion_scale
        self.sway_freq = random.uniform(0.4, 1.3)
        self.sway_phase = random.uniform(0, math.tau)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-25, 25)
        self.scale = random.uniform(0.7, 1.25)
        self.screen_height = screen_height
        self.offscreen_margin = 120 * motion_scale

    def update(self, dt):
        self.y += self.vy * dt
        self.angle += self.spin * dt

    def draw(self, surface, time):
        sway = math.sin(time * self.sway_freq + self.sway_phase) * self.sway_amp
        image = pygame.transform.rotozoom(self.base, self.angle, self.scale)
        rect = image.get_rect(center=(int(self.x + sway), int(self.y)))
        surface.blit(image, rect)

    def offscreen(self):
        return self.y > self.screen_height + self.offscreen_margin
