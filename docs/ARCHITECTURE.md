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
3. The engine creates a `960 × 800` logical display and then converts the remaining image assets for that display format.
4. Each frame processes input, spawns and updates entities, renders the pond and effects, and flips the display.
5. Exiting the loop shuts down Pygame cleanly.

## Modules

### `maple.engine`

Owns application lifetime, display modes, the event loop, spawn scheduling, entity collections, and frame composition. Fullscreen mode creates a borderless window at the current desktop resolution and scales the logical canvas to fill it without changing the monitor mode.

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

- The pond image defines the logical coordinate system.
- Mouse positions must stay in logical coordinates for ripple placement.
- A maximum ripple count bounds the most expensive NumPy work.
- Resource conversion must happen after the Pygame display is created.
- The package entry point and root launcher must remain equivalent.
