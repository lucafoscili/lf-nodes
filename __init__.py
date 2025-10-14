import sys
import os
import importlib.util

VERSION = "1.7.0"

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

MODULES_DIR = os.path.join(os.path.dirname(__file__), "modules")

sys.modules["lf_nodes"] = sys.modules[__name__]

for dirpath, _, filenames in os.walk(MODULES_DIR):
    for filename in filenames:
        if filename.endswith(".py") and filename != "__init__.py":
            relative_path = os.path.relpath(os.path.join(dirpath, filename), MODULES_DIR)
            module_name = os.path.splitext(relative_path.replace(os.path.sep, "."))[0]
            full_module_name = f"lf_nodes.modules.{module_name}"

            try:
                spec = importlib.util.spec_from_file_location(full_module_name, os.path.join(dirpath, filename))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    NODE_CLASS_MAPPINGS.update(getattr(module, "NODE_CLASS_MAPPINGS", {}))
                    NODE_DISPLAY_NAME_MAPPINGS.update(getattr(module, "NODE_DISPLAY_NAME_MAPPINGS", {}))
            except Exception as e:
                print(f"\033[31m❌ Failed to import {full_module_name}: {e}\033[0m")

WEB_DIRECTORY = "./web/deploy"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print("\033[34m*-----------------------------------------------------------*\033[0m")
print(f"\033[34m*             ✨ LF Nodes initialized - v{VERSION}              *\033[0m")
print("\033[34m*-----------------------------------------------------------*\033[0m")
