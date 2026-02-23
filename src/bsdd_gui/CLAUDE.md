# bsdd_gui Architecture

## Module System

Every module consists of a **core file**, a **tool file**, and a **module folder**.

### File layout

```
core/<module_name>.py          # Core implementation
tool/<module_name>.py          # Tool functions
module/<module_name>/
    __init__.py
    prop.py                    # Properties and data
    trigger.py                 # Event handlers / signal connections
    ui.py                      # UI setup and logic
```

### Call flow

```
trigger.py  -->  core functions  -->  tool functions  -->  trigger.py (callbacks)
```

- `trigger.py` calls functions from the corresponding `core/<module_name>.py`
- Core functions delegate lower-level operations to `tool/<module_name>.py`
- Tool functions may call back into `trigger.py` functions (e.g. to emit signals or update state)

### Qt UI files

Module folders may contain a `qt/` subfolder with:

- `.ui` files — Qt Designer source files
- `*_ui.py` files — precompiled Python versions generated from the `.ui` files

```
module/<module_name>/
    qt/
        Widget.ui
        Widget_ui.py           # precompiled
```

Use the precompiled `*_ui.py` versions at runtime; the `.ui` files are the designer source.
