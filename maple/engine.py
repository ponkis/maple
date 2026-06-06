import random
import pygame
import numpy as np

from maple.config import (
    FPS,
    MAX_RIPPLES,
    LEAF_INITIAL_COUNT,
    LEAF_SPAWN_INTERVAL
)
from maple.resources import ResourceManager
from maple.entities.leaf import Leaf
from maple.entities.ripple import Ripple

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
        self.screen = pygame.display.set_mode((self.W, self.H))
        
        # Professional window branding
        pygame.display.set_caption("maple")
        if self.resources.window_icon:
            pygame.display.set_icon(self.resources.window_icon)

        # Phase 3: Load/convert remaining runtime assets
        self.resources.load_runtime()
        self.pond_img = self.resources.pond_image

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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Spawn ripple and trigger a water splash sound
                    if len(self.ripples) >= MAX_RIPPLES:
                        self.ripples.pop(0)
                    self.ripples.append(Ripple(event.pos[0], event.pos[1]))
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

            pygame.display.flip()

        pygame.quit()
