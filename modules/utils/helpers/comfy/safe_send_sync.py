# region safe_send_sync
_CURRENT_CLIENT = object()


def normalize_node_id(node_id):
    """Unwrap Comfy's list-mode UNIQUE_ID value for frontend event routing."""

    while isinstance(node_id, (list, tuple)):
        if not node_id:
            return None
        node_id = node_id[0]
    return node_id


def get_current_client_id():
    """Return the client that owns the currently executing Comfy prompt."""
    try:
        from server import PromptServer

        client_id = PromptServer.instance.client_id
        if not isinstance(client_id, str):
            return None
        client_id = client_id.strip()
        return client_id or None
    except Exception:
        return None


def safe_send_sync(
    event: str,
    data: dict,
    node_id: str = None,
    *,
    target_client_id=_CURRENT_CLIENT,
):
    """
    Safely send a sync event to the frontend, with error handling for headless/container environments.

    This function wraps PromptServer.instance.send_sync with exception handling to prevent
    workflow execution from hanging in Docker containers or headless environments where
    WebSocket connections may not be available.

    Parameters:
    - event: The event name (without EVENT_PREFIX)
    - data: The data payload to send
    - node_id: Optional node ID for the event
    - target_client_id: Explicit client captured before deferred work begins.
      When omitted, the currently executing prompt owner is resolved at send time.
      An explicit ``None`` preserves the existing headless broadcast fallback.
    """
    try:
        from server import PromptServer
        from ...constants import EVENT_PREFIX
        payload = data.copy()
        node_id = normalize_node_id(node_id)
        if node_id is not None:
            payload["node"] = node_id
        client_id = (
            get_current_client_id()
            if target_client_id is _CURRENT_CLIENT
            else (
                target_client_id.strip()
                if isinstance(target_client_id, str) and target_client_id.strip()
                else None
            )
        )
        if client_id is None:
            PromptServer.instance.send_sync(f"{EVENT_PREFIX}{event}", payload)
        else:
            PromptServer.instance.send_sync(
                f"{EVENT_PREFIX}{event}",
                payload,
                client_id,
            )
    except Exception:
        # Silently ignore send_sync failures in headless/container environments
        # This prevents workflows from hanging when WebSocket infrastructure is unavailable
        pass
# endregion
