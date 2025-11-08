import aiohttp
import json
import os
import asyncio

from typing import Any

from server import PromptServer

from . import CATEGORY
from ...utils.constants import API_ROUTE_PREFIX, EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import clean_code_fences, create_ui_logger, parse_openai_json_output, parse_openai_response, read_secret

EVENT_NAME = f"{EVENT_PREFIX}openaiapi"

# region LF_OpenAIAPI
class LF_OpenAIAPI:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Text prompt to send to OpenAI."
                }),
            },
            "optional": {
                "model": (Input.STRING, {
                    "default": "gpt-4",
                    "tooltip": "OpenAI model to call."
                }),
                "system_message": (Input.STRING, {
                    "default": "You are a helpful assistant.",
                    "tooltip": "System message to set context."
                }),
                "temperature": (Input.FLOAT, {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "Controls randomness (0.0-2.0)."
                }),
                "max_tokens": (Input.INTEGER, {
                    "default": 1000,
                    "min": 1,
                    "max": 4096,
                    "tooltip": "Maximum tokens to generate."
                }),
                "timeout": (Input.INTEGER, {
                    "default": 60,
                    "tooltip": "Request timeout in seconds."
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Primary text output extracted from OpenAI response.",
        "Cleaned text output with code fences removed.",
        "Full OpenAI JSON response as string.",
        "Parsed JSON string when the output is valid JSON, otherwise empty.",
    )
    RETURN_NAMES = ("text", "clean", "raw_json", "json")
    RETURN_TYPES = (Input.STRING, Input.STRING, Input.JSON, Input.JSON)

    async def on_exec(self, **kwargs: dict) -> tuple[str, str]:
        prompt: str = kwargs.get("prompt", "")
        model: str = kwargs.get("model") or "gpt-4"
        system_message: str = kwargs.get("system_message") or "You are a helpful assistant."
        temperature: float = float(kwargs.get("temperature", 0.7))
        max_tokens: int = int(kwargs.get("max_tokens", 1000))
        logger = create_ui_logger(EVENT_NAME, kwargs.get("node_id"))

        logger.log("Sending request...")

        proxy_url = os.environ.get("OPENAI_PROXY_URL")
        if not proxy_url:
            try:
                ps_inst = getattr(PromptServer, 'instance', None)
                host = getattr(ps_inst, 'address', None)
                port = getattr(ps_inst, 'port', None)
                if host and port:
                    if host in ("0.0.0.0", "::"):
                        host = "localhost"
                    proxy_url = f"http://{host}:{port}{API_ROUTE_PREFIX}/proxy/openai"
                elif os.environ.get("DEV_ENV") == "1":
                    proxy_url = f"http://localhost:8080{API_ROUTE_PREFIX}/proxy/openai"
            except Exception:
                if os.environ.get("DEV_ENV") == "1":
                    proxy_url = f"http://localhost:8080{API_ROUTE_PREFIX}/proxy/openai"

        if not proxy_url:
            logger.log("No proxy URL configured. Set OPENAI_PROXY_URL environment variable or ensure PromptServer is running.")
            raise ValueError("No proxy URL configured. Set OPENAI_PROXY_URL environment variable or ensure PromptServer is running.")

        timeout_sec: int = int(kwargs.get("timeout", 60) or 60)

        if not prompt:
            logger.log("Prompt must not be empty.")
            raise ValueError("Prompt must not be empty.")

        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        headers = {"Content-Type": "application/json"}
        proxy_secret = read_secret("LF_PROXY_SECRET") or read_secret("OPENAI_PROXY_SECRET")
        if proxy_secret:
            headers["X-LF-Proxy-Secret"] = proxy_secret

        # Allow tests to inject a mocked aiohttp session via kwargs (dependency inversion for unit tests)
        injected_session = kwargs.get("_test_session")
        session_cm = injected_session if injected_session is not None else aiohttp.ClientSession()
        # Support both context-managed mock objects and real sessions
        async with session_cm as session:
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

        extracted = parse_openai_response(data)
        raw_json = json.dumps(data, ensure_ascii=False)
        clean_text = clean_code_fences(extracted)
        json_text = parse_openai_json_output(data, clean_text)

        logger.log("Request completed successfully.")

        return (extracted, clean_text, raw_json, json_text)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_OpenAIAPI": LF_OpenAIAPI,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_OpenAIAPI": "OpenAI API (Chat)",
}
# endregion