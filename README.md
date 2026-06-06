# maple

An interactive simulator of the classic **Android 4.0 Autumn Live Wallpaper**. Featuring realistic falling maple leaves, mouse-triggered water ripple calculations, and ambient water splash sound effects.

Developed by **ponkis**.

---

## Features

- **Leaf Simulation**: Dynamic falling leaf mechanics with custom swaying, scaling, and rotation.
- **Water Ripple Simulation**: Interactive ripple creation driven by high-performance NumPy array operations that compute coordinate displacements and shading updates on the water surface.
- **Branded Design**: Window captions, embedded app icon (`ico.ico`), and assets organized neatly.
- **Production Spec**: Ready-to-build configuration for standalone Windows executables.

---

## Architecture

The project is structured following clean architectural practices:

```
.
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt     # Python dependencies
├── main.py              # Root launcher wrapper
├── maple.spec           # PyInstaller build specification
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

Controls:
- **Mouse Click (Left Click)**: Create a water ripple at the cursor's location (triggers ambient water splash sounds).
- **Escape Key / Window Close**: Exit the application.

---

## Building Standalone Executable

To build a standalone `.exe` using PyInstaller:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Run PyInstaller with the spec file**:
   ```bash
   pyinstaller maple.spec
   ```

The compiled binary will be placed inside the `dist/maple/` or `dist/maple.exe` directory. It packages all images and audio files internally, requiring no extra assets folders to run.

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
