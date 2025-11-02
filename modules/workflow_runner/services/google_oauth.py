import aiohttp
import logging
import os

from typing import Optional, Dict, List

LOG = logging.getLogger(__name__)

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

# region ID token verification
async def verify_id_token_with_google(id_token: str, expected_audiences: Optional[List[str]] = None) -> Optional[Dict]:
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

                aud = data.get("aud")
                if expected_audiences:
                    if isinstance(aud, list):
                        ok = any(a in expected_audiences for a in aud)
                    else:
                        ok = aud in expected_audiences
                    if not ok:
                        LOG.warning("ID token aud (%s) not in allowed audiences", aud)
                        return None

                email = data.get("email")
                email_verified = data.get("email_verified") in ("true", "True", True, "1", 1)
                if not email:
                    LOG.warning("ID token missing email claim")
                    return None

                data["email_verified"] = email_verified
                return data
    except Exception as e:
        LOG.exception("Failed to verify id token with Google: %s", e)
        return None
# endregion

# region Allowed users loader
def load_allowed_users_from_file(path: str) -> List[str]:
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
# endregion