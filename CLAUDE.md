# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

bSDD-Toolkit is a dual-package Python project for working with buildingSMART Data Dictionary (bSDD) JSON:

- **`bsdd_json`** — Pydantic v2 data model with validation, URI parsing, and hierarchy utilities
- **`bsdd_gui`** — PySide6 GUI application for creating and editing bSDD dictionaries

## Commands

**Setup (uv workspace):**
```bash
uv sync                        # Install all workspace packages
pip install -e src/bsdd_gui[dev]   # Editable install with dev deps
```

**Run the GUI:**
```bash
python -m bsdd_gui                         # Start empty
python -m bsdd_gui path/to/file.json       # Open file
python -m bsdd_gui --open_last_project
python -m bsdd_gui --offline_mode
python -m bsdd_gui -l 10                   # Set log level (DEBUG=10)
```

**Tests:**
```bash
pytest                         # All tests (paths from pytest.ini)
pytest src/bsdd_json/tests/    # Data model tests only
pytest src/bsdd_gui/tests/     # GUI tests only
pytest src/bsdd_gui/tests/test_foo.py::test_bar  # Single test
```

**Lint / Format / Type check:**
```bash
ruff check .
black .
mypy src
```

**Build standalone executable:**
```bash
pyinstaller main.spec -y       # Output: src/dist/bSDD-Toolkit/
```

## Architecture

### Data Model (`src/bsdd_json/`)

Pydantic v2 models with an alias generator (JSON keys are PascalCase, Python attributes are snake_case):

- `BsddDictionary` — top-level container
- `BsddClass` — class node with parent/child weak references
- `BsddProperty` — property definition with data type and allowed values
- `BsddClassProperty` — links a class to a property (overrides and constraints)
- `BsddClassRelation` / `BsddPropertyRelation` — cross-reference edges
- `BsddAllowedValue` — enumerated values

Utilities in `utils/` handle class hierarchy traversal, property lookups, and URI parsing/building.

### GUI Application (`src/bsdd_gui/`)

#### Three-layer module system

Every feature lives in three places:

```
core/<module_name>.py          # Business logic and orchestration
tool/<module_name>.py          # Low-level accessor/mutator functions (public API)
module/<module_name>/
    __init__.py                # Registration hooks
    prop.py                    # Module-scoped state/data
    trigger.py                 # Qt signal connections and event handlers
    ui.py                      # Widget setup and composition
    qt/                        # Qt Designer .ui files + precompiled *_ui.py
```

Call flow: `trigger.py` → `core/<name>.py` → `tool/<name>.py` → back to `trigger.py` (callbacks/signals).

Always use the precompiled `*_ui.py` at runtime; `.ui` files are the Qt Designer source.

#### Module registration

`bsdd_gui/__init__.py` auto-discovers and imports all `module/*/` packages on startup:

1. `register()` — called once; `main_window_widget` must register first
2. `load_ui_triggers()` — wires all Qt signals after all modules are registered
3. Lifecycle hooks: `on_new_project()`, `retranslate_ui()`

When adding a new module, follow the existing pattern: create `core/`, `tool/`, and `module/<name>/` with the four standard files, then let auto-discovery pick it up.

#### Key modules

| Module | Role |
|---|---|
| `project` | File I/O, JSON load/save |
| `class_tree_view` | Hierarchical class browser (drag & drop) |
| `class_editor_widget` | Class creation/editing form |
| `property_table_widget` | Property editing tables |
| `class_property_table_view` | Class↔property linking |
| `allowed_values_table_view` | Enum value editing |
| `ai_helper` | OpenAI integration for generating descriptions |
| `excel` | Excel import/export (async with progress) |
| `ids_exporter` | IDS (Information Delivery Specification) export |
| `iso_export` | ISO 23386 export |
| `download` | Fetch dictionaries from buildingSMART registry |
| `ifc_helper` | IFC entity relationship tools |
| `plugins` | Plugin loading system |
| `search_widget` | Full-text fuzzy search |

### Ruff line-length

- `bsdd_gui`: 100 characters
- `bsdd_json`: 150 characters
