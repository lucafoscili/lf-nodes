import aiohttp
import html
import json
import os

from typing import Any

from server import PromptServer

from . import CATEGORY
from ...utils.constants import API_ROUTE_PREFIX, EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import clean_code_fences, create_ui_logger, parse_gemini_response, parse_json_from_text, read_secret

EVENT_NAME = f"{EVENT_PREFIX}geminiapi"

# region LF_GeminiAPI
class LF_GeminiAPI:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Text prompt to send to Gemini."
                }),
            },
            "optional": {
                "model": (Input.STRING, {
                    "default": "gemini-2.0-flash",
                    "tooltip": "Gemini model to call."
                }),
                "timeout": (Input.INTEGER, {
                    "default": 60,
                    "tooltip": "Request timeout in seconds."
                }),
                "ui_widget": (Input.LF_CODE, {
                    "default": "",
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Primary text output extracted from Gemini response (may include code fences).",
        "Cleaned text output with code fences removed (plain SVG or text).",
        "Full Gemini JSON response as string.",
        "Parsed JSON string when the output is valid JSON, otherwise empty.",
    )
    RETURN_NAMES = ("text", "clean", "raw_json", "json")
    RETURN_TYPES = (Input.STRING, Input.STRING, Input.JSON, Input.JSON)

    async def on_exec(self, **kwargs: dict) -> tuple[str, str]:
        prompt: str = kwargs.get("prompt", "")
        model: str = kwargs.get("model") or "gemini-2.0-flash"
        logger = create_ui_logger(EVENT_NAME, kwargs.get("node_id"))

        logger.log("Sending request...")

        proxy_url = os.environ.get("GEMINI_PROXY_URL")
        if not proxy_url:
            try:
                ps_inst = getattr(PromptServer, 'instance', None)
                host = getattr(ps_inst, 'address', None)
                port = getattr(ps_inst, 'port', None)
                if host and port:
                    if host in ("0.0.0.0", "::"):
                        host = "localhost"
                    proxy_url = f"http://{host}:{port}{API_ROUTE_PREFIX}/proxy/gemini"
                elif os.environ.get("DEV_ENV") == "1":
                    proxy_url = f"http://localhost:8080{API_ROUTE_PREFIX}/proxy/gemini"
            except Exception:
                if os.environ.get("DEV_ENV") == "1":
                    proxy_url = f"http://localhost:8080{API_ROUTE_PREFIX}/proxy/gemini"

        if not proxy_url:
            logger.log("No proxy URL configured. Set GEMINI_PROXY_URL environment variable or ensure PromptServer is running.")
            raise ValueError("No proxy URL configured. Set GEMINI_PROXY_URL environment variable or ensure PromptServer is running.")

        timeout_sec: int = int(kwargs.get("timeout", 60) or 60)

        if not prompt:
            logger.log("Prompt must not be empty.")
            raise ValueError("Prompt must not be empty.")

        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "model": model
        }

        headers = {"Content-Type": "application/json"}
        proxy_secret = read_secret("LF_PROXY_SECRET") or read_secret("GEMINI_PROXY_SECRET")
        if proxy_secret:
            headers["X-LF-Proxy-Secret"] = proxy_secret

        async with aiohttp.ClientSession() as session:
            async with session.post(proxy_url, headers=headers, json=payload, timeout=timeout_sec) as resp:
                text_status = await resp.text()
                try:
                    data = await resp.json()
                except Exception:
                    logger.log("Failed to parse JSON response.")
                    wrapper = {"body": text_status, "lf_http_status": resp.status}
                    return (text_status, json.dumps(wrapper, ensure_ascii=False))

        if isinstance(data, dict):
            data.setdefault("lf_http_status", resp.status)
        else:
            data = {"response": data, "lf_http_status": resp.status}

        logger.log("Request completed successfully.")

        extracted = parse_gemini_response(data)

        raw_json = json.dumps(data, ensure_ascii=False)

        clean_text = clean_code_fences(extracted)

        json_text = ""

        parsed = None
        try:
            parsed = parse_json_from_text(clean_text)
        except Exception:
            parsed = None

        if parsed is None and extracted:
            try:
                parsed = parse_json_from_text(extracted)
            except Exception:
                parsed = None

        if parsed is None:
            try:
                candidates = data.get('candidates') if isinstance(data, dict) else None
                if candidates and isinstance(candidates, list) and len(candidates) > 0:
                    first = candidates[0]
                    if isinstance(first, dict):
                        out = first.get('output')
                        if isinstance(out, (dict, list)):
                            parsed = out
                        elif isinstance(out, str):
                            parsed = parse_json_from_text(out)

                        if parsed is None and isinstance(first.get('content'), list):
                            txt = ''.join([chunk.get('text', '') for chunk in first.get('content', []) if isinstance(chunk, dict)])
                            parsed = parse_json_from_text(txt)

                if parsed is None and isinstance(data, dict) and isinstance(data.get('response'), dict):
                    out = data['response'].get('output')
                    if isinstance(out, (dict, list)):
                        parsed = out
                    elif isinstance(out, str):
                                                    parsed = parse_json_from_text(txt)
            except Exception:
                parsed = None

        if parsed is not None:
            try:
                json_text = json.dumps(parsed, ensure_ascii=False)
            except Exception:
                json_text = ''

        if json_text:
            try:
                json_text = html.unescape(json_text)
            except Exception:
                pass

        PromptServer.instance.send_sync(f"{EVENT_NAME}", {
            "node": kwargs.get("node_id"),
            "value": json_text,
        })

        return (extracted, clean_text, raw_json, json_text)

# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_GeminiAPI": LF_GeminiAPI,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_GeminiAPI": "Gemini API (Google)",
}
# endregion
