import math
import numpy as np
import pygame
from maple.config import (
    RIPPLE_R_CAP,
    RIPPLE_LIFE,
    RIPPLE_SPEED,
    RIPPLE_AMP,
    RIPPLE_WAVELENGTH,
    RIPPLE_RING_WIDTH
)

class Ripple:
    """
    Simulates water surface ripples using coordinate displacement 
    and lighting reflection/refraction calculated via NumPy.
    """
    __slots__ = ("cx", "cy", "age", "life", "speed", "amp",
                 "wavelength", "ring_width")

    def __init__(self, x, y):
        self.cx = float(x)
        self.cy = float(y)
        self.age = 0.0
        self.life = RIPPLE_LIFE
        self.speed = RIPPLE_SPEED
        self.amp = RIPPLE_AMP
        self.wavelength = RIPPLE_WAVELENGTH
        self.ring_width = RIPPLE_RING_WIDTH

    def update(self, dt):
        self.age += dt

    def alive(self):
        return self.age < self.life

    def render(self, target, pond_arr):
        time_decay = max(0.0, 1.0 - self.age / self.life)
        if time_decay < 0.05:
            return
        
        # Determine background dimensions from the array shape
        H, W, _ = pond_arr.shape
        
        peak_r = self.age * self.speed
        R = min(peak_r + self.ring_width, RIPPLE_R_CAP)
        x0 = max(0, int(self.cx - R))
        x1 = min(W, int(self.cx + R + 1))
        y0 = max(0, int(self.cy - R))
        y1 = min(H, int(self.cy + R + 1))
        if x0 >= x1 or y0 >= y1:
            return

        h_local = y1 - y0
        w_local = x1 - x0

        ys = np.arange(y0, y1, dtype=np.float32)[:, None] - np.float32(self.cy)
        xs = np.arange(x0, x1, dtype=np.float32)[None, :] - np.float32(self.cx)
        dist = np.sqrt(xs * xs + ys * ys)

        delta = dist - np.float32(peak_r)
        sigma = np.float32(self.ring_width * 0.5)
        envelope = np.exp(-(delta * delta) / (np.float32(2.0) * sigma * sigma))
        grow = np.float32(min(1.0, self.age * 4.0))
        amp_field = np.float32(self.amp) * envelope * np.float32(time_decay) * grow

        k = np.float32(2.0 * math.pi / self.wavelength)
        phase = delta * k
        wave = np.sin(phase) * amp_field

        safe_dist = np.maximum(dist, np.float32(0.5))
        dx = (xs / safe_dist) * wave
        dy = (ys / safe_dist) * wave

        iy = np.arange(y0, y1, dtype=np.int32)[:, None]
        ix = np.arange(x0, x1, dtype=np.int32)[None, :]
        src_y = np.clip(iy + np.rint(dy).astype(np.int32), 0, H - 1)
        src_x = np.clip(ix + np.rint(dx).astype(np.int32), 0, W - 1)

        sampled = pond_arr[src_y, src_x]

        slope = np.cos(phase) * amp_field * k
        highlight = np.clip(slope * np.float32(18.0), -55, 90).astype(np.int16)

        shaded = sampled.astype(np.int16) + highlight[..., None]
        np.clip(shaded, 0, 255, out=shaded)
        displaced = shaded.astype(np.uint8)

        # Alpha mask: blend strength = envelope * time_decay, so edges fade to 0
        blend = envelope * np.float32(time_decay) * grow
        alpha = np.clip(blend * 255.0, 0.0, 255.0).astype(np.uint8)

        local = pygame.Surface((w_local, h_local), pygame.SRCALPHA)
        arr = pygame.surfarray.pixels3d(local)
        arr[:, :, :] = displaced.swapaxes(0, 1)
        del arr
        alpha_arr = pygame.surfarray.pixels_alpha(local)
        alpha_arr[:, :] = alpha.T
        del alpha_arr

        target.blit(local, (x0, y0))
