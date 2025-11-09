# region safe_send_sync
def safe_send_sync(event: str, data: dict, node_id: str = None):
    """
    Safely send a sync event to the frontend, with error handling for headless/container environments.

    This function wraps PromptServer.instance.send_sync with exception handling to prevent
    workflow execution from hanging in Docker containers or headless environments where
    WebSocket connections may not be available.

    Parameters:
    - event: The event name (without EVENT_PREFIX)
    - data: The data payload to send
    - node_id: Optional node ID for the event
    """
    try:
        from server import PromptServer
        from ...constants import EVENT_PREFIX
        payload = data.copy()
        if node_id:
            payload["node"] = node_id
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}{event}", payload)
    except Exception:
        # Silently ignore send_sync failures in headless/container environments
        # This prevents workflows from hanging when WebSocket infrastructure is unavailable
        pass
# endregion