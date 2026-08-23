import random
import sys

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
        self.base_size = self.resources.pond_raw.get_size()
        self.W, self.H = self.base_size

        # Phase 2: Create and brand the initial window
        self.fullscreen = False
        self.display = self._create_display()
        self.window = Window.from_display_module()
        pygame.display.set_caption("maple")
        if self.resources.window_icon:
            pygame.display.set_icon(self.resources.window_icon)

        # Phase 3: Load runtime assets and generate the initial scene
        self.resources.load_runtime()
        self.pond_source = self.resources.pond_image
        self.clock = pygame.time.Clock()
        self.leaves = []
        self.ripples = []
        self.spawn_acc = 0.0
        self._rebuild_scene(self.display.get_size())

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            t = pygame.time.get_ticks() / 1000.0

            mode_changed = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_f, pygame.K_F11):
                        mode_changed = self.toggle_fullscreen() or mode_changed
                    elif event.key == pygame.K_ESCAPE:
                        if self.fullscreen:
                            mode_changed = self.toggle_fullscreen() or mode_changed
                        else:
                            running = False
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and not mode_changed
                ):
                    if len(self.ripples) >= MAX_RIPPLES:
                        self.ripples.pop(0)
                    self.ripples.append(
                        Ripple(event.pos[0], event.pos[1], self.scene_scale)
                    )
                    if self.resources.ripple_sounds:
                        random.choice(self.resources.ripple_sounds).play()

            self.spawn_acc += dt
            while self.spawn_acc >= self.leaf_spawn_interval:
                self.spawn_acc -= self.leaf_spawn_interval
                self.leaves.append(
                    Leaf(self.W, self.H, self.leaf_variants, self.scene_scale)
                )

            for leaf in self.leaves:
                leaf.update(dt)
            self.leaves = [leaf for leaf in self.leaves if not leaf.offscreen()]

            for ripple in self.ripples:
                ripple.update(dt)
            self.ripples = [ripple for ripple in self.ripples if ripple.alive()]

            self.screen.blit(self.pond_img, (0, 0))
            for ripple in self.ripples:
                ripple.render(self.screen, self.pond_rgb)
            for leaf in self.leaves:
                leaf.draw(self.screen, t)

            pygame.display.flip()

        pygame.quit()

    def _create_display(self):
        """Create the initial native-size display."""
        return pygame.display.set_mode(self.base_size)

    @staticmethod
    def _cover_surface(source, size):
        """Create a target-sized background using one uniform scale and center crop."""
        target_width, target_height = size
        source_width, source_height = source.get_size()
        scale = max(target_width / source_width, target_height / source_height)
        scaled_size = (
            max(target_width, round(source_width * scale)),
            max(target_height, round(source_height * scale)),
        )
        scaled = pygame.transform.smoothscale(source, scaled_size)
        background = pygame.Surface(size).convert()
        background.blit(
            scaled,
            (
                (target_width - scaled_size[0]) // 2,
                (target_height - scaled_size[1]) // 2,
            ),
        )
        return background

    def _rebuild_scene(self, size):
        """Regenerate render surfaces and simulation entities at the active resolution."""
        self.W, self.H = size
        self.screen = self.display

        base_width, base_height = self.base_size
        self.scene_scale = min(self.W / base_width, self.H / base_height)
        self.pond_img = self._cover_surface(self.pond_source, size)
        self.pond_rgb = (
            pygame.surfarray.array3d(self.pond_img).swapaxes(0, 1).copy()
        )
        self.leaf_variants = self.resources.leaf_variants_for_scale(
            self.scene_scale
        )

        self.ripples.clear()
        self.leaves.clear()
        self.spawn_acc = 0.0

        density_scale = (self.W * self.H) / (
            base_width * base_height * self.scene_scale * self.scene_scale
        )
        self.leaf_spawn_interval = LEAF_SPAWN_INTERVAL / max(1.0, density_scale)
        initial_count = max(
            LEAF_INITIAL_COUNT,
            round(LEAF_INITIAL_COUNT * density_scale),
        )
        for _ in range(initial_count):
            leaf = Leaf(
                self.W,
                self.H,
                self.leaf_variants,
                self.scene_scale,
            )
            leaf.y = random.uniform(-200 * self.scene_scale, self.H)
            self.leaves.append(leaf)

    def toggle_fullscreen(self):
        """Toggle SDL desktop fullscreen and rebuild the scene at its resolution."""
        target = not self.fullscreen
        try:
            if target:
                self.window.set_fullscreen(desktop=True)
            else:
                self.window.set_windowed()
        except pygame.error as error:
            print(f"Could not change fullscreen mode: {error}", file=sys.stderr)
            return False

        self.fullscreen = target
        pygame.event.pump()
        pygame.display.get_window_size()
        self.display = pygame.display.get_surface()
        self._rebuild_scene(self.display.get_size())
        return True
