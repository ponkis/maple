import os
import sys
import pygame
from maple.config import RIPPLE_SOUND_VOLUME, TARGET_LEAF_SIZE, LEAF_W, LEAF_H

def get_asset_path(filename):
    """
    Resolve asset paths transparently across development 
    and packaged environments (PyInstaller).
    """
    if hasattr(sys, "_MEIPASS"):
        # Extracted location for PyInstaller
        return os.path.join(sys._MEIPASS, "maple", "assets", filename)
    else:
        # Development location relative to package path
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", filename)

class ResourceManager:
    """
    Handles asset loading and pre-processing.
    Supports a two-phase loading process to accommodate Pygame's display requirements.
    """
    def __init__(self):
        self.pond_raw = None
        self.pond_image = None
        self.window_icon = None
        self.leaf_variants = []
        self.ripple_sounds = []

    def load_initial(self):
        """
        Load the raw assets required for window setup (dimensions and icon).
        No display conversions are done here.
        """
        pond_path = get_asset_path("pond.jpg")
        if not os.path.exists(pond_path):
            raise FileNotFoundError(f"Required asset not found: {pond_path}")
        self.pond_raw = pygame.image.load(pond_path)

        icon_path = get_asset_path("ico.ico")
        if os.path.exists(icon_path):
            self.window_icon = pygame.image.load(icon_path)

    def load_runtime(self):
        """
        Convert assets and load remaining sound effects.
        Must be called AFTER pygame.display.set_mode has been initialized.
        """
        if self.pond_raw is None:
            raise RuntimeError("load_initial() must be called before load_runtime()")

        # Convert pond image using the active display mode
        self.pond_image = self.pond_raw.convert()
        self.pond_raw = None  # Free raw texture memory

        # Load leaves and slice individual variants
        leaves_path = get_asset_path("leaves.png")
        if not os.path.exists(leaves_path):
            raise FileNotFoundError(f"Required asset not found: {leaves_path}")
        leaves_sheet = pygame.image.load(leaves_path).convert_alpha()
        
        self.leaf_variants = []
        for i in range(8):
            sub = pygame.Surface((LEAF_W, LEAF_H), pygame.SRCALPHA)
            sub.blit(leaves_sheet, (0, 0), (i * LEAF_W, 0, LEAF_W, LEAF_H))
            sub = pygame.transform.smoothscale(sub, (TARGET_LEAF_SIZE, TARGET_LEAF_SIZE))
            self.leaf_variants.append(sub)

        # Load sound effects
        self.ripple_sounds = []
        for i in range(1, 5):
            sound_path = get_asset_path(f"ripple{i}.mp3")
            if os.path.exists(sound_path):
                snd = pygame.mixer.Sound(sound_path)
                snd.set_volume(RIPPLE_SOUND_VOLUME)
                self.ripple_sounds.append(snd)
