"""Lightweight Google ID token verification helper.

This module implements ID token verification by calling Google's
tokeninfo endpoint (https://oauth2.googleapis.com/tokeninfo?id_token=<token>).

Design notes:
- Uses aiohttp already present in the project; no extra dependencies.
- This is intentionally a pragmatic approach (not full JWKS signature
  verification) suitable for short-lived dev sharing and small teams.
  For production, prefer validating JWT signatures locally against
  Google's JWKS.
"""
from __future__ import annotations

import os
import logging
from typing import Optional, Dict, List

import aiohttp

LOG = logging.getLogger(__name__)

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


async def verify_id_token_with_google(id_token: str, expected_audiences: Optional[List[str]] = None) -> Optional[Dict]:
    """Verify an ID token by calling Google's tokeninfo endpoint.

    Returns the token claims dict if valid, otherwise None.

    expected_audiences: optional list of allowed client IDs (aud).
    If provided, the token's aud must match one of these.
    """
    if not id_token:
        return None

    params = {"id_token": id_token}
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(GOOGLE_TOKENINFO_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    LOG.debug("google tokeninfo returned status %s: %s", resp.status, text)
                    return None
                data = await resp.json()

                # tokeninfo returns audience as 'aud'
                aud = data.get("aud")
                if expected_audiences:
                    if isinstance(aud, list):
                        ok = any(a in expected_audiences for a in aud)
                    else:
                        ok = aud in expected_audiences
                    if not ok:
                        LOG.warning("ID token aud (%s) not in allowed audiences", aud)
                        return None

                # require email_verified or presence of email
                email = data.get("email")
                email_verified = data.get("email_verified") in ("true", "True", True, "1", 1)
                if not email:
                    LOG.warning("ID token missing email claim")
                    return None

                # tokeninfo may not include email_verified for some tokens; be permissive if the client trusts it
                data["email_verified"] = email_verified
                return data
    except Exception as e:
        LOG.exception("Failed to verify id token with Google: %s", e)
        return None


def load_allowed_users_from_file(path: str) -> List[str]:
    """Load allowed users (email addresses) from a file (one per line).

    Returns a lowercased list with whitespace trimmed and comments ignored.
    """
    try:
        if not path or not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh.readlines()]
        users = [l.lower() for l in lines if l and not l.startswith("#")]
        return users
    except Exception:
        LOG.exception("Failed to load allowed users file: %s", path)
        return []
