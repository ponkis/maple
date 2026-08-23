import os
import sys

import pygame

from maple.config import (
    LEAF_H,
    LEAF_VARIANTS_COUNT,
    LEAF_W,
    RIPPLE_SOUND_VOLUME,
    TARGET_LEAF_SIZE,
)


def get_asset_path(filename):
    """
    Resolve asset paths transparently across development and PyInstaller environments.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "maple", "assets", filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", filename)


class ResourceManager:
    """
    Load and preprocess application assets after Pygame initializes its display.
    """

    def __init__(self):
        self.pond_raw = None
        self.pond_image = None
        self.window_icon = None
        self.leaf_sources = []
        self.leaf_variants = []
        self.ripple_sounds = []

    def load_initial(self):
        """Load assets needed before display-dependent surface conversion."""
        pond_path = get_asset_path("pond.jpg")
        if not os.path.exists(pond_path):
            raise FileNotFoundError(f"Required asset not found: {pond_path}")
        self.pond_raw = pygame.image.load(pond_path)

        icon_path = get_asset_path("ico.ico")
        if os.path.exists(icon_path):
            self.window_icon = pygame.image.load(icon_path)

    def load_runtime(self):
        """Convert display assets, split leaf sources, and load splash audio."""
        if self.pond_raw is None:
            raise RuntimeError("load_initial() must be called before load_runtime()")

        self.pond_image = self.pond_raw.convert()
        self.pond_raw = None

        leaves_path = get_asset_path("leaves.png")
        if not os.path.exists(leaves_path):
            raise FileNotFoundError(f"Required asset not found: {leaves_path}")
        leaves_sheet = pygame.image.load(leaves_path).convert_alpha()

        self.leaf_sources = []
        for index in range(LEAF_VARIANTS_COUNT):
            rect = pygame.Rect(index * LEAF_W, 0, LEAF_W, LEAF_H)
            self.leaf_sources.append(leaves_sheet.subsurface(rect).copy())
        self.leaf_variants = self.leaf_variants_for_scale(1.0)

        self.ripple_sounds = []
        for index in range(1, 5):
            sound_path = get_asset_path(f"ripple{index}.mp3")
            if os.path.exists(sound_path):
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(RIPPLE_SOUND_VOLUME)
                self.ripple_sounds.append(sound)

    def leaf_variants_for_scale(self, scale):
        """Regenerate leaf surfaces for the active scene resolution."""
        if not self.leaf_sources:
            raise RuntimeError("load_runtime() must be called before scaling leaves")

        size = max(1, round(TARGET_LEAF_SIZE * max(float(scale), 0.01)))
        return [
            pygame.transform.smoothscale(source, (size, size))
            for source in self.leaf_sources
        ]
