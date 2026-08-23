# Architecture

Maple is a small, single-process desktop simulation. It intentionally keeps the runtime direct: Pygame owns the window and event loop, NumPy performs localized pixel calculations, and a few entity classes carry animation state.

## Runtime flow

```text
main.py / python -m maple
          |
          v
       Engine
       /  |  \
      /   |   \
resources events entities
      |     |      |
    assets  |   Leaf / Ripple
            v
       update + render
            |
            v
       Pygame display
```

1. `maple.__main__` creates an `Engine`.
2. `ResourceManager.load_initial()` loads the pond and icon before the display exists.
3. The engine creates the initial `960 × 800` display and converts immutable source assets for that display format.
4. A fullscreen transition reacquires the desktop-sized display and regenerates the pond surface, NumPy source buffer, leaf artwork, population, and pixel-based effect metrics at that native size.
5. Each frame processes native input coordinates, updates entities, renders directly into the active display surface, and flips it.
6. Exiting the loop shuts down Pygame cleanly.

## Modules

### `maple.engine`

Owns application lifetime, display modes, the event loop, native-resolution scene regeneration, spawn scheduling, entity collections, and frame composition. SDL desktop fullscreen expands the window to the monitor bounds without changing its display mode. The engine then renders directly at those dimensions; it does not enlarge a finished frame.

### `maple.resources`

Resolves files relative to the source package or PyInstaller's temporary bundle directory. Its two-phase loader avoids converting surfaces before a display format exists.

### `maple.entities.leaf`

Stores the randomized state for one falling leaf. The engine supplies elapsed time, and each leaf handles its own movement and drawing.

### `maple.entities.ripple`

Calculates displacement and highlights only inside a bounded region around one ripple. Limiting the work to that region avoids rebuilding the entire pond surface for each effect.

### `maple.config`

Contains the simulation constants used by the engine and entities. It has no runtime state or persistence.

## Assets and packaging

Runtime assets live in `maple/assets`. The Python package metadata includes them for wheel builds, while `maple.spec` includes them in the standalone Windows executable. Keep those two manifests aligned when adding an asset type.

## Design constraints

- The original pond image remains an immutable raster source; a display-sized background is generated from it once per mode change.
- Scene dimensions always match the active display surface, so mouse positions are already ripple coordinates.
- A maximum ripple count bounds the most expensive NumPy work.
- Resource conversion must happen after the Pygame display is created.
- The package entry point and root launcher must remain equivalent.
