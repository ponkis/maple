import math
import random
import sys

import numpy as np
import pygame
from pygame._sdl2 import Window

from maple.config import (
    FPS,
    MAX_RIPPLES,
    LEAF_INITIAL_COUNT,
    LEAF_SPAWN_INTERVAL,
)
from maple.entities.leaf import Leaf
from maple.entities.ripple import Ripple
from maple.resources import ResourceManager


class Engine:
    """
    Main application engine coordinating Pygame setup, events, simulation logic, and rendering.
    """
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Phase 1: Load initial assets for layout and branding setup
        self.resources = ResourceManager()
        self.resources.load_initial()

        # Phase 2: Create window using loaded dimensions
        self.W, self.H = self.resources.pond_raw.get_size()
        self.fullscreen = False
        self.display = self._create_display()
        self.window = Window.from_display_module()
        self._update_viewport()

        # Professional window branding
        pygame.display.set_caption("maple")
        if self.resources.window_icon:
            pygame.display.set_icon(self.resources.window_icon)

        # Phase 3: Load/convert remaining runtime assets
        self.resources.load_runtime()
        self.pond_img = self.resources.pond_image
        self.screen = pygame.Surface((self.W, self.H)).convert()

        self.clock = pygame.time.Clock()
        self.pond_rgb = pygame.surfarray.array3d(self.pond_img).swapaxes(0, 1).copy()

        self.leaves = []
        self.ripples = []
        self.spawn_acc = 0.0

        # Spawn initial scatter of leaves
        for _ in range(LEAF_INITIAL_COUNT):
            leaf = Leaf(self.W, self.H, self.resources.leaf_variants)
            leaf.y = random.uniform(-200, self.H)
            self.leaves.append(leaf)

    def run(self):
        running = True
        while running:
            # Regulate tick rate and retrieve delta time
            dt = self.clock.tick(FPS) / 1000.0
            t = pygame.time.get_ticks() / 1000.0

            # 1. Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_f, pygame.K_F11):
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        if self.fullscreen:
                            self.toggle_fullscreen()
                        else:
                            running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    position = self._logical_position(event.pos)
                    if position is None:
                        continue

                    # Spawn ripple and trigger a water splash sound
                    if len(self.ripples) >= MAX_RIPPLES:
                        self.ripples.pop(0)
                    self.ripples.append(Ripple(*position))
                    if self.resources.ripple_sounds:
                        random.choice(self.resources.ripple_sounds).play()

            # 2. Spawning updates
            self.spawn_acc += dt
            while self.spawn_acc >= LEAF_SPAWN_INTERVAL:
                self.spawn_acc -= LEAF_SPAWN_INTERVAL
                self.leaves.append(Leaf(self.W, self.H, self.resources.leaf_variants))

            # 3. Update physics and boundaries
            for leaf in self.leaves:
                leaf.update(dt)
            self.leaves = [l for l in self.leaves if not l.offscreen()]

            for r in self.ripples:
                r.update(dt)
            self.ripples = [r for r in self.ripples if r.alive()]

            # 4. Rendering
            self.screen.blit(self.pond_img, (0, 0))
            for r in self.ripples:
                r.render(self.screen, self.pond_rgb)
            for leaf in self.leaves:
                leaf.draw(self.screen, t)

            self._present()

        pygame.quit()

    def _create_display(self):
        """Create the initial native-size display."""
        return pygame.display.set_mode((self.W, self.H))

    def _update_viewport(self):
        """Fill fullscreen without distortion by uniformly scaling and cropping."""
        display_width, display_height = self.display.get_size()
        if not self.fullscreen:
            self.viewport = pygame.Rect(0, 0, display_width, display_height)
            return

        scale = max(display_width / self.W, display_height / self.H)
        width = math.ceil(self.W * scale)
        height = math.ceil(self.H * scale)
        self.viewport = pygame.Rect(
            (display_width - width) // 2,
            (display_height - height) // 2,
            width,
            height,
        )

    def _logical_position(self, position):
        """Map a display position into the simulation's logical coordinates."""
        if not self.viewport.collidepoint(position):
            return None

        x = (position[0] - self.viewport.x) * self.W / self.viewport.width
        y = (position[1] - self.viewport.y) * self.H / self.viewport.height
        return min(self.W - 1, int(x)), min(self.H - 1, int(y))

    def _present(self):
        """Copy the canvas to the window or aspect-fill the fullscreen display."""
        if self.fullscreen:
            frame = pygame.transform.smoothscale(self.screen, self.viewport.size)
            self.display.blit(frame, self.viewport)
        else:
            self.display.blit(self.screen, (0, 0))
        pygame.display.flip()

    def toggle_fullscreen(self):
        """Toggle SDL desktop fullscreen without changing the monitor mode."""
        target = not self.fullscreen
        try:
            if target:
                self.window.set_fullscreen(desktop=True)
            else:
                self.window.set_windowed()
        except pygame.error as error:
            print(f"Could not change fullscreen mode: {error}", file=sys.stderr)
            return

        self.fullscreen = target
        pygame.event.pump()
        pygame.display.get_window_size()
        self.display = pygame.display.get_surface()
        self._update_viewport()
