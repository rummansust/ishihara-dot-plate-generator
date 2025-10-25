

# Ishihara Dot Plate Game

This is a desktop game for testing color vision using Ishihara-style plates.

## How to Run

1. **Install dependencies:**
	- Python 3.x
	- Pillow
	- customtkinter
	- (Tkinter is included with most Python installations)
   
	You can install dependencies with:
	```sh
	pip install pillow customtkinter
	```

2. **Run the game:**
	```sh
	"""
	# Ishihara Dot Plate Game

	This is a desktop game for testing color vision using Ishihara-style plates.

	## Prerequisites

	- Python 3.8+ (3.13 used in development) installed
	- A working audio setup for sound feedback (macOS users see note below)

	## Quick setup (recommended)

	1. Create and activate a virtual environment:

	```sh
	python -m venv .venv
	source .venv/bin/activate
	```

	2. Install dependencies:

	- Using requirements.txt:

	```sh
	pip install -r requirements.txt
	```

	- Or install the package in editable/develop mode (recommended for development):

	```sh
	pip install -e .
	```

	The project also contains `pyproject.toml` with the same runtime dependencies.

	## Running the frontend (GUI)

	The GUI is a Tkinter/customtkinter app located under `src/app/gui/`.

	Preferred (Makefile helper):

	```sh
	# from project root
	make run
	```

	Run directly with Python if you prefer:

	```sh
	# from project root
	source .venv/bin/activate
	python -m src.app.gui.main_window
	```

	If your environment doesn't support `-m` for that path, run the module file directly:

	```sh
	python src/app/gui/main_window.py
	```

	## Running the backend (plate generation / CLI)

	There are library modules under `src/app/` that can be used programmatically to generate plates or run CLI tasks. Typical usage:

	```py
	from app import plates
	plate = plates.generate_plate(...)
	# see module docstrings for parameter details
	```

	If there is an explicit CLI entrypoint provided by the package, install editable mode (`pip install -e .`) and run the console script (if present). Otherwise, import the modules as shown above in a small script.

	## Sound on macOS

	The project uses `playsound` for simple playback. On modern macOS + Python versions, `playsound` falls back to launching another Python process unless `pyobjc` is installed. If you don't hear sounds on macOS, install `pyobjc` in your venv:

	```sh
	pip install pyobjc
	```

	The `requirements.txt` and `pyproject.toml` include `playsound` and `pyobjc` to help with this.

	## Test the sound quickly

	You can run a tiny script that attempts to play the sample correct sound included in the repo:

	```sh
	source .venv/bin/activate
	/path/to/venv/bin/python src/app/gui/test_sound.py
	```

	It will print the absolute path to the sound file before trying to play it.

	## Notes and troubleshooting

	- If `playsound` raises an error about Python 2 on macOS or cannot find `/System/Library/Frameworks/Python.framework/Versions/2.7/bin/python`, install `pyobjc` in the active venv.
	- If sounds still don't play, verify your system audio and that the .mp3 files exist under `src/resources/`.
	- If you hit import issues when running modules with `-m`, ensure your working directory is the project root and your venv is active.

	If you want, I can add small wrapper scripts/console entry points (e.g., `console_scripts`) to simplify running backend tasks and the GUI.
	"""

