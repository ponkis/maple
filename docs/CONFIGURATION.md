# Configuration

Maple has no user settings file. Its behavior is tuned through constants in `maple/config.py`; restart the application after changing them.

## Frame timing

| Constant | Default | Purpose |
| --- | ---: | --- |
| `FPS` | `60` | Target frame rate for the main loop |

Physics updates use delta time, so leaf and ripple speed remain broadly consistent when a frame takes longer than expected.

## Leaves

| Constant | Default | Purpose |
| --- | ---: | --- |
| `LEAF_W` | `128` | Width of one source sprite-sheet cell |
| `LEAF_H` | `128` | Height of one source sprite-sheet cell |
| `TARGET_LEAF_SIZE` | `108` | Preprocessed size of each leaf variant |
| `LEAF_VARIANTS_COUNT` | `8` | Number of variants in the sheet |
| `LEAF_INITIAL_COUNT` | `8` | Leaves scattered across the initial scene |
| `LEAF_SPAWN_INTERVAL` | `0.85` | Seconds between new leaves |

Individual fall speed, sway, rotation, and scale ranges are defined in `maple/entities/leaf.py` because they are part of each entity's behavior.

## Ripples

| Constant | Default | Purpose |
| --- | ---: | --- |
| `MAX_RIPPLES` | `3` | Maximum simultaneous ripples |
| `RIPPLE_R_CAP` | `150.0` | Maximum processed radius in pixels |
| `RIPPLE_SOUND_VOLUME` | `0.45` | Splash sample volume from `0.0` to `1.0` |
| `RIPPLE_LIFE` | `1.5` | Lifetime in seconds |
| `RIPPLE_SPEED` | `80.0` | Outward movement in pixels per second |
| `RIPPLE_AMP` | `7.0` | Displacement amplitude |
| `RIPPLE_WAVELENGTH` | `38.0` | Spacing between wave peaks |
| `RIPPLE_RING_WIDTH` | `60.0` | Width of the processed wave envelope |

Larger ripple radii, widths, or simultaneous counts increase per-frame NumPy work. Change one group at a time and test both windowed and fullscreen input alignment.

## Display

The pond asset determines the `960 × 800` logical resolution. There is intentionally no display setting or on-screen fullscreen button:

- `F` and `F11` toggle fullscreen.
- `Esc` returns to windowed mode before it quits the application.
- Maple stretches the logical canvas across a borderless window at the current desktop resolution and maps pointer coordinates back into the simulation.

Replacing `pond.jpg` with another resolution changes the simulation bounds. Test leaf spawning, ripple edges, and fullscreen scaling after doing so.
