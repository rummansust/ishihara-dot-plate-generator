
# Ishihara Dot Plate Generator

This project is a Python application for generating Ishihara-style color vision test plates, designed for color blindness (color vision deficiency) testing. It is especially suitable for children who can recognize numbers (1-10) and capital letters (A-Z).

## Purpose

The Ishihara Dot Plate Generator helps parents, educators, and healthcare professionals test color vision in a fun, interactive way. It allows easy creation of custom Ishihara plates using pre-stored binary masks for each character, and supports a simple test workflow with navigation, answer input, and scoring.

## How It Works

- **Binary Masks:** Each number or letter is represented as a binary (0/1) image, stored as text or Python lists. 1 means inside the shape, 0 means background.
- **Dot Rendering:** The app draws colored dots (with varying size and shade) to fill the shape and background, using different color palettes for each.
- **Flood Fill/Threshold:** Dots are placed so that the shape is preserved, with a threshold to avoid overflow and maintain clarity.
- **User Interface:** The app allows users to go to the next/previous plate, enter answers, and see their score.

## Features

- Pre-stored binary masks for 1-10 and A-Z
- Randomized dot size, position, and color shade for realism
- Easy-to-use GUI (Tkinter)
- Manual answer entry and scoring
- Extensible for more shapes or custom plates

## Installation

1. **Clone the repository:**
	```sh
	git clone https://github.com/yourusername/ishihara-dot-plate-generator.git
	cd ishihara-dot-plate-generator
	```
2. **Install dependencies:**
	Ensure you have Python 3.x installed. Then install required packages:
	```sh
	pip install pillow
	```
	Tkinter is included with most Python installations. If not, install it via your OS package manager.

## Usage

Run the main script to launch the application:

```sh
python main.py
```

Follow the on-screen instructions to navigate plates, enter answers, and view your score.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements or new features.

## License

This project is licensed under the MIT License.

---

See `chat_summary.md` for ongoing design and discussion.

