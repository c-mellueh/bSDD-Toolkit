import logging
import os
import argparse

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), keep_trailing_newline=True)


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def _render(template_name: str, **kwargs) -> str:
    return _env.get_template(template_name).render(**kwargs)


def create_module(name: str):
    module_path = os.path.abspath(os.path.join(os.curdir, "module", name))
    tool_name = to_camel_case(name)
    prop_name = f"{to_camel_case(name)}Properties"
    widget_name = "Widget"
    ctx = {"name": name, "tool_name": tool_name, "prop_name": prop_name, "widget_name": widget_name}

    if os.path.exists(module_path):
        logging.warning("Module already exists")
    else:
        os.mkdir(module_path)

    init_path = os.path.join(module_path, "__init__.py")
    if os.path.exists(init_path):
        logging.warning("__init__.py already exists")
    with open(init_path, "w") as f:
        f.write(_render("init.txt", **ctx))

    prop_path = os.path.join(module_path, "prop.py")
    if os.path.exists(prop_path):
        logging.warning("prop.py already exists")
    with open(prop_path, "w") as f:
        f.write(_render("prop.txt", **ctx))

    trigger_path = os.path.join(module_path, "trigger.py")
    if os.path.exists(trigger_path):
        logging.warning("trigger.py already exists")
    with open(trigger_path, "w") as f:
        f.write(_render("trigger.txt", **ctx))

    ui_path = os.path.join(module_path, "ui.py")
    if os.path.exists(ui_path):
        logging.warning("ui.py already exists")
    with open(ui_path, "w") as f:
        f.write(_render("ui.txt", **ctx))


def create_core(name: str):
    tool_name = to_camel_case(name)
    widget_name = "Widget"
    ctx = {"name": name, "tool_name": tool_name, "widget_name": widget_name}
    core_path = os.path.abspath(os.path.join(os.curdir, "core", f"{name}.py"))
    if os.path.exists(core_path):
        logging.warning("core.py already exists")
    with open(core_path, "w") as f:
        f.write(_render("core.txt", **ctx))


def create_tool(name: str):
    tool_path = os.path.abspath(os.path.join(os.curdir, "tool", f"{name}.py"))
    tool_name = to_camel_case(name)
    prop_name = f"{to_camel_case(name)}Properties"
    widget_name = "Widget"
    ctx = {"name": name, "tool_name": tool_name, "prop_name": prop_name, "widget_name": widget_name}

    if os.path.exists(tool_path):
        logging.warning("tool.py already exists")
    with open(tool_path, "w") as f:
        f.write(_render("tool.txt", **ctx))


def main(name: str):
    os.chdir("bsdd_gui")
    create_core(name)
    create_tool(name)
    create_module(name)


# Create the parser
parser = argparse.ArgumentParser(description="Script to run a module with a name argument")

# Add the "name" argument
parser.add_argument("name", type=str, help="Name of the module to run")

# Parse the arguments
args = parser.parse_args()
if __name__ == "__main__":
    main(args.name)
    # you need to add module to tool.__init__.py by hand
