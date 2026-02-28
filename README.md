# Geogebra
Geogebra (Pygame Implementation)
A lightweight geometric drawing and interaction tool developed based on the Python Pygame framework, replicating the core functions of the classic Geogebra (e.g., drawing, selecting, and deleting basic geometric shapes like points, lines, and circles). It is packaged as a Windows executable file and can be used directly without configuring a development environment.
🌟 Core Features
Lightweight: Built on the Pygame 2D graphics engine, featuring small size and fast startup;
Easy to Use: Provides a Windows executable file (Geogebra.exe) that can be launched with a double-click;
Interactive: Supports drawing, selection, and deletion of basic geometric shapes (points, lines, circles, etc.);
Extensible: Decoupled code structure for easy addition of new shape types, interaction logic, or functional modules;
Logging: Built-in logging module to record program running status and error information for easy debugging.
📁 Directory Structure
plaintext
├── .gitignore          # Git ignore rules configuration
├── LICENSE             # Open source license
├── README.md           # Project documentation (this file)
├── pyvenv.cfg          # Python virtual environment configuration
├── setting.json        # Program runtime configuration (window size, drawing parameters, etc.)
├── exe/                # Executable program directory
│   └── Geogebra.exe    # Windows executable file (run directly)
├── code/               # Core code directory
│   ├── const.py        # Constant definitions (colors, sizes, key mappings, etc.)
│   ├── geogebra.py     # Core business logic (geometric drawing/interaction)
│   ├── log.py          # Log module (runtime logs/error records)
│   ├── main.py         # Program entry (Pygame initialization/main loop/event handling)
│   └── sprites.py      # Sprite class (graphic rendering/collision detection)
├── img/                # Image resources (buttons, graphic assets, program icon)
│   ├── SHobject.png
│   ├── choose.png
│   └── icon.ico
└── ttf/                # Font resources (interface text rendering)
    ├── JetBrainsMono-2.304/
    └── WenJinMinchoP0-Regular.ttf
🚀 Quick Start
Method 1: Run the Executable File (Recommended)
Navigate to the exe/ directory in the repository;
Double-click Geogebra.exe to launch the tool;
After startup, use the mouse/keyboard to draw, select, or delete geometric shapes.
Method 2: Development & Debugging (Run from Source)
Ensure Python 3.x is installed locally;
Activate the project's virtual environment (refer to pyvenv.cfg for configuration);
Install dependencies:
bash
pip install pygame
Run the core entry file:
bash
python code/main.py
⚙️ Configuration Notessetting.jsonon: Custom program configuration file; modify window size, default drawing parameters, log level, etc. (restart the program for changes to take effect);{insert\_element\_1\_Ci0gYGNvZGUvY29uc3Qu}py: Built-in constants (e.g., color values, key mappings, default graphic sizes) that can be adjusted during development.
📝 Development Notes
**Core Logicgeogebra.py.py implements geometric calculation and interacti{insert\_element\_3\_b247IGBzcHJpdGVz}.py handles graphic rendering via Pygame Sprite;
**Event Handlingmain.py.py` listens for mouse/keyboard events to drive graphic interaction logic;
Log Viewing: Program runtime logs are managedlog.py.py`; configure log output level/path as needed.
📄 License
This project is governed by the open source license defined inLICENSEENSE` file in the root directory of the repository. You are free to use, modify, and distribute the code in accordance with the license terms.
📌 Future Expansion
Add more geometric shapes (polygons, ellipses, parabolas, etc.);
Implement graphic property editing (color, thickness, labels, etc.);
Add graphic calculation functions (distance, angle, area, etc.);
Supplement operation guides, shortcut key instructions, and other interactive prompts.