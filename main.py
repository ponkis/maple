import math
import os
import random
import sys

import numpy as np
import pygame

def resource_path(filename):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def main():
    pygame.init()
    pygame.mixer.init()

    pond_raw = pygame.image.load(resource_path("pond.jpg"))
    W, H = pond_raw.get_size()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("live")

    icon_path = resource_path("icon.png")
    if os.path.exists(icon_path):
        pygame.display.set_icon(pygame.image.load(icon_path))

    clock = pygame.time.Clock()
    pond_img = pond_raw.convert()
    leaves_sheet = pygame.image.load(resource_path("leaves.png")).convert_alpha()

    ripple_sounds = []
    for i in range(1, 5):
        path = resource_path(f"ripple{i}.mp3")
        if os.path.exists(path):
            snd = pygame.mixer.Sound(path)
            snd.set_volume(0.45)
            ripple_sounds.append(snd)

    LEAF_W, LEAF_H = 128, 128
    leaf_variants = []
    for i in range(8):
        sub = pygame.Surface((LEAF_W, LEAF_H), pygame.SRCALPHA)
        sub.blit(leaves_sheet, (0, 0), (i * LEAF_W, 0, LEAF_W, LEAF_H))
        sub = pygame.transform.smoothscale(sub, (108, 108))
        leaf_variants.append(sub)

    pond_rgb = pygame.surfarray.array3d(pond_img).swapaxes(0, 1).copy()

    class Leaf:
        __slots__ = ("base", "x", "y", "vy", "sway_amp", "sway_freq",
                     "sway_phase", "angle", "spin", "scale")

        def __init__(self):
            self.base = random.choice(leaf_variants)
            self.x = random.uniform(-40, W + 40)
            self.y = random.uniform(-160, -40)
            self.vy = random.uniform(18, 42)
            self.sway_amp = random.uniform(15, 55)
            self.sway_freq = random.uniform(0.4, 1.3)
            self.sway_phase = random.uniform(0, math.tau)
            self.angle = random.uniform(0, 360)
            self.spin = random.uniform(-25, 25)
            self.scale = random.uniform(0.7, 1.25)

        def update(self, dt):
            self.y += self.vy * dt
            self.angle += self.spin * dt

        def draw(self, surf, t):
            sway = math.sin(t * self.sway_freq + self.sway_phase) * self.sway_amp
            img = pygame.transform.rotozoom(self.base, self.angle, self.scale)
            rect = img.get_rect(center=(int(self.x + sway), int(self.y)))
            surf.blit(img, rect)

        def offscreen(self):
            return self.y > H + 120

    MAX_RIPPLES = 3
    RIPPLE_R_CAP = 150.0

    class Ripple:
        __slots__ = ("cx", "cy", "age", "life", "speed", "amp",
                     "wavelength", "ring_width")

        def __init__(self, x, y):
            self.cx = float(x)
            self.cy = float(y)
            self.age = 0.0
            self.life = 1.5
            self.speed = 80.0
            self.amp = 7.0
            self.wavelength = 38.0
            self.ring_width = 60.0

        def update(self, dt):
            self.age += dt

        def alive(self):
            return self.age < self.life

        def render(self, target, pond_arr):
            time_decay = max(0.0, 1.0 - self.age / self.life)
            if time_decay < 0.05:
                return
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

    leaves = []
    ripples = []
    spawn_acc = 0.0
    SPAWN_INTERVAL = 0.85

    for _ in range(8):
        leaf = Leaf()
        leaf.y = random.uniform(-200, H)
        leaves.append(leaf)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        t = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if len(ripples) >= MAX_RIPPLES:
                    ripples.pop(0)
                ripples.append(Ripple(event.pos[0], event.pos[1]))
                if ripple_sounds:
                    random.choice(ripple_sounds).play()

        spawn_acc += dt
        while spawn_acc >= SPAWN_INTERVAL:
            spawn_acc -= SPAWN_INTERVAL
            leaves.append(Leaf())

        for leaf in leaves:
            leaf.update(dt)
        leaves = [l for l in leaves if not l.offscreen()]

        for r in ripples:
            r.update(dt)
        ripples = [r for r in ripples if r.alive()]

        screen.blit(pond_img, (0, 0))
        for r in ripples:
            r.render(screen, pond_rgb)
        for leaf in leaves:
            leaf.draw(screen, t)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
