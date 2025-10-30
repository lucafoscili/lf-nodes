"""Compatibility shim for google_oauth helpers moved into services."""

from .services.google_oauth import *  # re-export implementation

__all__ = ["verify_id_token_with_google", "load_allowed_users_from_file"]
