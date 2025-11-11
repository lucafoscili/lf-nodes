# region ui_logger
"""
UI Logger for real-time feedback in ComfyUI nodes.

This logger is designed for any node that performs async operations and needs to provide
real-time feedback to users via LF_CODE widgets. It's not limited to LLM operations.

Usage examples:
- API calls (LLM, image generation, etc.)
- File processing operations
- Batch processing with progress updates
- Long-running computations
- Network requests

Example:
    from ...utils.helpers.api import create_ui_logger

    logger = create_ui_logger(f"{EVENT_PREFIX}myoperation", node_id)
    logger.log("Starting operation...")
    # ... do work ...
    logger.log("Operation completed!")
"""
import json
from typing import Any

from ....utils.helpers.comfy import safe_send_sync

class UILogger:
    """
    Helper class for logging operations with real-time UI updates.
    Useful for any async operations that need to provide feedback via LF_CODE widgets.
    """

    def __init__(self, event_name: str, node_id: str):
        self.event_name = event_name
        self.node_id = node_id
        self.log_lines: list[str] = []

    def log(self, value: str | dict) -> None:
        """
        Logs a message and sends it to the UI via PromptServer.

        Args:
            value: The message to log (string or dict that will be JSON-serialized)
        """
        if isinstance(value, dict):
            try:
                value = json.dumps(value, ensure_ascii=False)
            except Exception:
                value = str(value)

        self.log_lines.append(value)
        full_log = "\n\n".join(self.log_lines)

        safe_send_sync(self.event_name, {
            "node": self.node_id,
            "value": full_log,
        }, self.node_id)

    def get_full_log(self) -> str:
        """Returns the complete log as a single string."""
        return "\n\n".join(self.log_lines)

def create_ui_logger(event_name: str, node_id: str) -> UILogger:
    """
    Factory function to create a UI logger.

    Args:
        event_name: Unprefixed event name for PromptServer updates
        node_id: The node ID for UI targeting

    Returns:
        A configured UILogger instance
    """
    return UILogger(event_name, node_id)
# endregion