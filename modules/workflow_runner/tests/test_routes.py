"""Placeholder tests for route wiring.

These will be expanded once controllers are wired into the server. For now
this test ensures importability of the controllers package.
"""
from ..controllers import api_controllers


def test_controllers_importable():
    assert hasattr(api_controllers, "start_workflow_controller")
