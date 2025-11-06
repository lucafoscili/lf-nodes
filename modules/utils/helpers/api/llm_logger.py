# region llm_logger
import json
from typing import Any

from server import PromptServer

class LLMLogger:
    """
    Helper class for logging LLM API interactions with real-time UI updates.
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

        PromptServer.instance.send_sync(self.event_name, {
            "node": self.node_id,
            "value": full_log,
        })

    def get_full_log(self) -> str:
        """Returns the complete log as a single string."""
        return "\n\n".join(self.log_lines)

def create_llm_logger(event_name: str, node_id: str) -> LLMLogger:
    """
    Factory function to create an LLM logger.

    Args:
        event_name: The event name for PromptServer updates
        node_id: The node ID for UI targeting

    Returns:
        A configured LLMLogger instance
    """
    return LLMLogger(event_name, node_id)
# endregion