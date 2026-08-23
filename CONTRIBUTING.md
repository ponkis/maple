# Contributing

Thank you for helping improve Maple. Small, focused changes are easiest to review.

## Set up a development environment

```bash
git clone https://github.com/ponkis/maple.git
cd maple
python -m venv .venv
```

Activate the environment, then install the runtime and build dependencies:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

Run the application with `python -m maple`.

## Before submitting a change

1. Keep simulation constants in `maple/config.py` and resource resolution in `maple/resources.py`.
2. Preserve both supported entry points: `python -m maple` and `python main.py`.
3. If assets change, keep `pyproject.toml` and `maple.spec` package-data rules aligned.
4. Verify syntax and imports:

   ```bash
   python -m compileall -q main.py maple
   python -c "import maple; import maple.engine"
   ```

5. Run the app and exercise ripple placement, `F`/`F11`, `Esc`, and window close behavior.
6. For packaging changes, build with `pyinstaller --clean maple.spec` and launch the result from `dist`.

## Pull requests

- Explain the user-facing effect and motivation.
- Keep unrelated cleanup out of the change.
- Update the README or files in `docs/` when controls, architecture, or configuration change.
- Include screenshots for visual changes when they make the result easier to review.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
