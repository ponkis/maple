<div align="center">

# maple

An interactive recreation of the Android 4.0 Autumn live wallpaper.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/pygame-2.x-0D8F45)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

Maple brings the calm pond, falling leaves, and touch-driven ripples of the classic wallpaper to a lightweight native desktop window.

## Features

- Procedural leaves with independent fall speed, sway, rotation, and scale.
- Localized NumPy water displacement, shading, and fading ripple rings.
- Responsive splash audio selected from multiple ambient samples.
- Keyboard-only fullscreen that regenerates the animated scene at the active display resolution.
- Asset loading that works from source and from a PyInstaller executable.
- A compact package layout separated by runtime responsibility.

---

## Architecture

The project is structured following clean architectural practices:

```
.
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── docs/                # Architecture and configuration notes
├── requirements.txt     # Python dependencies
├── main.py              # Root launcher wrapper
├── maple.spec           # PyInstaller build specification
├── pyproject.toml       # Python project metadata
└── maple/               # Package root
    ├── __init__.py      # Versioning & author metadata
    ├── __main__.py      # Package execution entry point
    ├── config.py        # Centralized settings and constants
    ├── resources.py     # Caching resource loader (dev & build environment safe)
    ├── engine.py        # Pygame loop orchestration
    ├── assets/          # Application media assets (images, sounds, icons)
    └── entities/        # Entity simulation logic
        ├── __init__.py
        ├── leaf.py      # Leaf physics and drawing logic
        └── ripple.py    # NumPy water ripple simulation calculations
```
See [Architecture](docs/ARCHITECTURE.md) for the runtime data flow and [Configuration](docs/CONFIGURATION.md) for tuning constants.

---

## Requirements

- Python 3.8+
- Pygame 2.x
- NumPy 1.x / 2.x

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ponkis/maple.git
   cd maple
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

You can start the simulator in one of two ways:

- **Via the root wrapper**:
  ```bash
  python main.py
  ```

- **Directly as a module**:
  ```bash
  python -m maple
  ```

## Controls

| Input | Action |
| --- | --- |
| Left click | Create a ripple and play a splash sound |
| `F` or `F11` | Toggle fullscreen |
| `Esc` | Leave fullscreen; quit when already windowed |
| Window close | Quit |

Fullscreen is deliberately keyboard-only. On a mode change, Maple rebuilds its render surface, pond buffer, NumPy ripple source, leaf artwork, population, and effect metrics at the actual display dimensions. Frames are then drawn directly to the display without scaling a completed viewport. The fixed pond bitmap is fitted once with a uniform cover and center crop because it is the only raster source.

---

## Building Standalone Executable

To build a standalone `.exe` using PyInstaller:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Run PyInstaller with the spec file**:
   ```bash
   pyinstaller --clean maple.spec
   ```

The standalone application is written to `dist/maple.exe`. Images, audio, and the window icon are bundled by `maple.spec`.

## Contributing and security

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md), and follow the [Code of Conduct](CODE_OF_CONDUCT.md) in project spaces.

## License

Maple is available under the [MIT License](LICENSE).
