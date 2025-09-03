# bSDD-Toolkit

Visual editor and Python toolkit for working with buildingSMART Data Dictionary (bSDD) JSON.

This repository contains:
- A validated data model for bSDD JSON (Pydantic v2) under `src/bsdd_parser`.
- A PySide6 GUI to create, view, and edit bSDD dictionaries under `src/bsdd_gui`.


## Features
- Edit dictionaries: classes, property sets, properties, and allowed values.
- Class tree with drag & drop and quick search.
- Property set and property tables with sorting and inline editing where supported.
- Relationship and IFC helpers (modules present for extension).
- Modular architecture with a lightweight plugin system.
- Multilingual-ready UI (German translation scaffold included).


## Requirements
- Python 3.10+
- Pip and a virtual environment are recommended
- Platform dependencies for Qt (PySide6) as required by your OS


## Installation

Clone the repository and install the package (editable for development or standard install):

```bash
git clone https://github.com/<your-org-or-user>/bsdd-creator.git
cd bsdd-creator

# (optional) create and activate a virtualenv
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# install
pip install -U pip
pip install -e .            # for development
# or
pip install .               # for a regular install

# dev extras
pip install -e .[dev]       # ruff, black, mypy, pytest, etc.
```


## Run the GUI

Run the application module directly (optionally pass a path to a bSDD JSON file to open):

```bash
python -m bsdd_gui                   # start empty
python -m bsdd_gui som-0.2.0.json    # open example dictionary
```

Command-line options supported by the launcher:

```text
python -m bsdd_gui [open_path] [-l LOG_LEVEL] [--open_last_project]

open_path           Optional path to a bSDD JSON file
-l, --log-level     Integer log level (e.g. 10=DEBUG, 20=INFO)
--open_last_project Open the last project on startup
```


## Screenshots

Add the PNGs to `docs/images/` with the names below. They will render automatically in GitHub once added.

### Main Window
![Main UI](docs/images/main-ui.png)

### Editors
| Edit Properties | Edit Classes |
| --- | --- |
| <img src="docs/images/edit-properties.png" alt="Editing Properties" width="400"> | <img src="docs/images/edit-classes.png" alt="Editing Classes" width="400"> |


## Use the Data Model (Python)

Load, inspect, and write bSDD JSON using the Pydantic models:

```python
from bsdd_parser import BsddDictionary, BsddClass, BsddProperty, BsddClassProperty

# Load and validate an existing dictionary (see som-0.2.0.json)
d = BsddDictionary.load("example.json")
print(d.DictionaryName, d.DictionaryVersion)

# Programmatically create a new dictionary
new_d = BsddDictionary(
    OrganizationCode="example",
    DictionaryCode="demo",
    DictionaryName="Demo Dictionary",
    DictionaryVersion="0.1.0",
    LanguageIsoCode="en-US",
    LanguageOnly=False,
    UseOwnUri=False,
)
# Create and add Classes
class_1 = BsddClass(Code="Wall", Name="Wall", ClassType="Class")
class_2 = BsddClass(Code="Slab", Name="Slab", ClassType="Class")
new_d.Classes += [class_1, class_2]

# Create and add Property
prop_1 = BsddProperty(Code="Height", Name="Height", DataType="Real")
new_d.Properties.append(prop_1)

# Create and add ClassProperties
class_1.ClassProperties.append(
    BsddClassProperty(Code="height", PropertyCode=prop_1.Code, PropertySet="Geometry")
)
class_2.ClassProperties.append(
    BsddClassProperty(Code="height", PropertyCode=prop_1.Code, PropertySet="Geometry")
)

# Serialize to JSON
new_d.save("example.json")
```


## Project Structure

- `src/bsdd_parser` — Pydantic models and helpers for bSDD JSON.
- `src/bsdd_gui` — PySide6 GUI application (run with `python -m bsdd_gui`).
  - `__main__.py` — entry point for the GUI launcher.
  - `module/` — feature modules (class tree, property tables, search, etc.).
  - `core/` — application wiring and shared UI logic.
  - `tool/` — helper functions that get called from /core.
  - `resources/` — icons, translations, and static assets.


## Development

Useful commands when developing locally:

```bash
# formatting & linting
ruff check .
black .

# type checking
mypy src

# run the GUI during development
python -m bsdd_gui
```

## License

MIT — see `LICENSE` for details.


## Acknowledgements

- buildingSMART International for the bSDD initiative and specifications.
