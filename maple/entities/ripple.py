import math

import numpy as np
import pygame

from maple.config import (
    RIPPLE_AMP,
    RIPPLE_LIFE,
    RIPPLE_R_CAP,
    RIPPLE_RING_WIDTH,
    RIPPLE_SPEED,
    RIPPLE_WAVELENGTH,
)


class Ripple:
    """
    Simulate a native-resolution water ripple with NumPy displacement and shading.
    """

    __slots__ = (
        "cx",
        "cy",
        "age",
        "life",
        "speed",
        "amp",
        "wavelength",
        "ring_width",
        "radius_cap",
    )

    def __init__(self, x, y, scene_scale=1.0):
        scale = max(float(scene_scale), 0.01)

        self.cx = float(x)
        self.cy = float(y)
        self.age = 0.0
        self.life = RIPPLE_LIFE
        self.speed = RIPPLE_SPEED * scale
        self.amp = RIPPLE_AMP * scale
        self.wavelength = RIPPLE_WAVELENGTH * scale
        self.ring_width = RIPPLE_RING_WIDTH * scale
        self.radius_cap = RIPPLE_R_CAP * scale

    def update(self, dt):
        self.age += dt

    def alive(self):
        return self.age < self.life

    def render(self, target, pond_arr):
        time_decay = max(0.0, 1.0 - self.age / self.life)
        if time_decay < 0.05:
            return

        height, width, _ = pond_arr.shape

        peak_radius = self.age * self.speed
        radius = min(peak_radius + self.ring_width, self.radius_cap)
        x0 = max(0, int(self.cx - radius))
        x1 = min(width, int(self.cx + radius + 1))
        y0 = max(0, int(self.cy - radius))
        y1 = min(height, int(self.cy + radius + 1))
        if x0 >= x1 or y0 >= y1:
            return

        local_height = y1 - y0
        local_width = x1 - x0

        ys = np.arange(y0, y1, dtype=np.float32)[:, None] - np.float32(self.cy)
        xs = np.arange(x0, x1, dtype=np.float32)[None, :] - np.float32(self.cx)
        distance = np.sqrt(xs * xs + ys * ys)

        delta = distance - np.float32(peak_radius)
        sigma = np.float32(self.ring_width * 0.5)
        envelope = np.exp(-(delta * delta) / (np.float32(2.0) * sigma * sigma))
        grow = np.float32(min(1.0, self.age * 4.0))
        amp_field = np.float32(self.amp) * envelope * np.float32(time_decay) * grow

        wave_number = np.float32(2.0 * math.pi / self.wavelength)
        phase = delta * wave_number
        wave = np.sin(phase) * amp_field

        safe_distance = np.maximum(distance, np.float32(0.5))
        dx = (xs / safe_distance) * wave
        dy = (ys / safe_distance) * wave

        iy = np.arange(y0, y1, dtype=np.int32)[:, None]
        ix = np.arange(x0, x1, dtype=np.int32)[None, :]
        source_y = np.clip(
            iy + np.rint(dy).astype(np.int32),
            0,
            height - 1,
        )
        source_x = np.clip(
            ix + np.rint(dx).astype(np.int32),
            0,
            width - 1,
        )
        sampled = pond_arr[source_y, source_x]

        slope = np.cos(phase) * amp_field * wave_number
        highlight = np.clip(slope * np.float32(18.0), -55, 90).astype(np.int16)

        shaded = sampled.astype(np.int16) + highlight[..., None]
        np.clip(shaded, 0, 255, out=shaded)
        displaced = shaded.astype(np.uint8)

        blend = envelope * np.float32(time_decay) * grow
        alpha = np.clip(blend * 255.0, 0.0, 255.0).astype(np.uint8)

        local = pygame.Surface((local_width, local_height), pygame.SRCALPHA)
        color_pixels = pygame.surfarray.pixels3d(local)
        color_pixels[:, :, :] = displaced.swapaxes(0, 1)
        del color_pixels

        alpha_pixels = pygame.surfarray.pixels_alpha(local)
        alpha_pixels[:, :] = alpha.T
        del alpha_pixels

        target.blit(local, (x0, y0))
