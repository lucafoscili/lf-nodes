from __future__ import annotations

import sys
import types

from modules.tests.common_mocks import scoped_common_mocks


with scoped_common_mocks(torch_enabled=True):
    base64_module = types.ModuleType(
        "modules.utils.helpers.conversion.base64_to_tensor"
    )
    base64_module.base64_to_tensor = lambda value: value
    sys.modules[base64_module.__name__] = base64_module
    from modules.nodes.llm.stability_api import LF_StabilityAPI  # noqa: E402

from modules.utils.constants import Input  # noqa: E402


def test_stability_api_exposes_the_code_logger_widget() -> None:
    schema = LF_StabilityAPI.INPUT_TYPES()

    assert schema["optional"]["ui_widget"] == (
        Input.LF_CODE,
        {"default": ""},
    )
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
