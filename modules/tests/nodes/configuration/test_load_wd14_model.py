import importlib
import sys


def test_wd14_node_registration_does_not_require_optional_timm(monkeypatch):
    module_name = "modules.nodes.configuration.load_wd14_model"
    sys.modules.pop(module_name, None)
    monkeypatch.setitem(sys.modules, "timm", None)

    module = importlib.import_module(module_name)

    assert "LF_LoadWD14Model" in module.NODE_CLASS_MAPPINGS
