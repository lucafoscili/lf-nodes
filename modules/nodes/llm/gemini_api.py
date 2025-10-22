import aiohttp
import html
import json
import os
import re

from typing import Any

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX
from ...utils.constants import FUNCTION, Input

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
                "api_key": (Input.STRING, {
                    "default": "",
                    "tooltip": "Google API key; leave empty to use environment variable GEMINI_API_KEY (recommended)."
                }),
                "proxy_url": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional server-side proxy URL to call instead of the Google endpoint. If set, the node will POST to this URL and will NOT send the X-goog-api-key header." 
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
        log: str = "## Gemini API Node Log\n"

        def _send_log(value: str | dict) -> None:
            nonlocal log
            if isinstance(value, dict):
                try:
                    value = json.dumps(value, ensure_ascii=False)
                except Exception:
                    value = str(value)
            log = f"{log}\n\n{value}"
            PromptServer.instance.send_sync(f"{EVENT_NAME}", {
                "node": kwargs.get("node_id"),
                "value": log,
            })

        def _read_secret(env_name: str) -> str | None:
            v = os.environ.get(env_name)
            if v:
                return v
            file_env = f"{env_name}_FILE"
            p = os.environ.get(file_env)
            if p and os.path.exists(p):
                try:
                    with open(p, 'r', encoding='utf-8') as fh:
                        return fh.read().strip()
                except Exception:
                    return None
            return None

        _send_log("Sending request...")

        api_key: str = kwargs.get("api_key") or _read_secret("GEMINI_API_KEY") or ""
        proxy_url: str = kwargs.get("proxy_url") or os.environ.get("GEMINI_PROXY_URL", "")
        if not proxy_url:
            if _read_secret("LF_PROXY_SECRET") or _read_secret("GEMINI_PROXY_SECRET"):
                env_proxy = os.environ.get("GEMINI_PROXY_URL")
                if env_proxy:
                    proxy_url = env_proxy
                else:
                    try:
                        ps_inst = getattr(PromptServer, 'instance', None)
                        host = getattr(ps_inst, 'address', None)
                        port = getattr(ps_inst, 'port', None)
                        if host and port:
                            proxy_url = f"http://{host}:{port}/api/proxy/gemini"
                        else:
                            if os.environ.get("DEV_ENV") == "1":
                                proxy_url = "http://localhost:8080/api/proxy/gemini"
                        _send_log("Using PromptServer proxy for Gemini API requests...")
                    except Exception:

                        _send_log("Could not determine PromptServer address for proxy; proceeding without proxy.")
                        if os.environ.get("DEV_ENV") == "1":
                            proxy_url = "http://localhost:8080/api/proxy/gemini"
        timeout_sec: int = int(kwargs.get("timeout", 60) or 60)

        if not prompt:
            _send_log("Prompt must not be empty.")
            raise ValueError("Prompt must not be empty.")

        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        if proxy_url:
            url = proxy_url
            headers = {"Content-Type": "application/json"}
            proxy_secret = _read_secret("LF_PROXY_SECRET") or _read_secret("GEMINI_PROXY_SECRET")
            if proxy_secret:
                headers["X-LF-Proxy-Secret"] = proxy_secret
        else:
            if not api_key:
                _send_log("No API key provided. Set the 'api_key' input or environment variable GEMINI_API_KEY, or configure a proxy via proxy_url/GEMINI_PROXY_URL.")
                raise ValueError("No API key provided. Set the 'api_key' input or environment variable GEMINI_API_KEY, or configure a proxy via proxy_url/GEMINI_PROXY_URL.")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": api_key,
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=timeout_sec) as resp:
                text_status = await resp.text()
                try:
                    data = await resp.json()
                except Exception:
                    _send_log("Failed to parse JSON response.")
                    wrapper = {"body": text_status, "lf_http_status": resp.status}
                    return (text_status, json.dumps(wrapper, ensure_ascii=False))

        if isinstance(data, dict):
            data.setdefault("lf_http_status", resp.status)
        else:
            data = {"response": data, "lf_http_status": resp.status}

        _send_log("Request completed successfully.")

        extracted = ""
        try:
            candidates = data.get("candidates") or []
            if candidates and isinstance(candidates, list):
                first = candidates[0]
                if isinstance(first, dict):
                    if "content" in first:
                        if isinstance(first["content"], list):
                            extracted = "".join([chunk.get("text", "") for chunk in first["content"] if isinstance(chunk, dict)])
                        else:
                            extracted = str(first.get("content", ""))
                    elif "output" in first:
                        extracted = json.dumps(first["output"])
                    else:
                        extracted = str(first)
            else:
                if "response" in data and isinstance(data["response"], dict):
                    out = data["response"].get("output")
                    if isinstance(out, list):
                        extracted = "\n".join([str(x) for x in out])
                    else:
                        extracted = str(out or "")
        except Exception:
            extracted = str(data)

        raw_json = json.dumps(data, ensure_ascii=False)

        clean_text = extracted
        try:
            if clean_text.startswith('```') and '```' in clean_text[3:]:
                end = clean_text.rfind('```')
                inner = clean_text[3:end]
                inner_lines = inner.splitlines()
                if len(inner_lines) > 0 and inner_lines[0].strip().isalpha():
                    inner = '\n'.join(inner_lines[1:])
                clean_text = inner.strip()
            else:
                clean_text = clean_text.replace('`', '').strip()
        except Exception:
            clean_text = extracted

        json_text = ""

        def _try_parse_json_from_string(s: str):
            if not s:
                return None
            s0 = s.strip()
            try:
                _send_log("Attempting to parse JSON from string...")
                return json.loads(s0)
            except Exception:
                pass

            s1 = s0.replace('\\/', '/')
            try:
                s2 = bytes(s1, 'utf-8').decode('unicode_escape')
            except Exception:
                _send_log("Failed to decode unicode escape.")
                s2 = s1

            m = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', s2)
            if m:
                candidate = m.group(1)
                try:
                    return json.loads(candidate)
                except Exception:
                    pass

            try:
                return json.loads(s2)
            except Exception:
                return None

        parsed = None
        try:
            parsed = _try_parse_json_from_string(clean_text)
        except Exception:
            parsed = None

        if parsed is None and extracted:
            try:
                parsed = _try_parse_json_from_string(extracted)
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
                            parsed = _try_parse_json_from_string(out)

                        if parsed is None and isinstance(first.get('content'), list):
                            txt = ''.join([chunk.get('text', '') for chunk in first.get('content', []) if isinstance(chunk, dict)])
                            parsed = _try_parse_json_from_string(txt)

                if parsed is None and isinstance(data, dict) and isinstance(data.get('response'), dict):
                    out = data['response'].get('output')
                    if isinstance(out, (dict, list)):
                        parsed = out
                    elif isinstance(out, str):
                        parsed = _try_parse_json_from_string(out)
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
