# region handle_response
def handle_response(response: dict, method: str = "GET"):
    """
    Handles the response from a Language Model (LLM) endpoint and tries to
    extract a human-usable string result from common response shapes.

    Supports (in order of preference):
      - OpenAI-style: { choices: [ { message: { content: ... } } ] }
      - OpenAI legacy-style: { choices: [ { text: ... } ] }
      - Top-level `text` string
      - `result` or `output` fields
      - `generations` / `generation` lists with `text` entries

    Returns a tuple (status_code, method, message).
    """
    try:
        status = int(getattr(response, "status_code", getattr(response, "status", None)))
    except Exception:
        status = None

    if status == 400:
        return status, method, "Bad Request"
    if status == 401:
        return status, method, "Unauthorized"
    if status == 403:
        return status, method, "Forbidden"
    if status == 404:
        return status, method, "Not Found"
    if status == 500:
        return status, method, "Internal Server Error"

    if status == 200:
        try:
            llm_result = response.json()
        except Exception:
            try:
                content = getattr(response, "content", None)
                if isinstance(content, (bytes, bytearray)):
                    return status, method, content.decode("utf-8", errors="replace")
            except Exception:
                pass
            return status, method, "Whoops! Something went wrong."

        try:
            if isinstance(llm_result, dict) and "choices" in llm_result and len(llm_result["choices"]) > 0:
                first = llm_result["choices"][0]
                # OpenAI chat-style
                if isinstance(first, dict) and "message" in first and isinstance(first["message"], dict) and "content" in first["message"]:
                    return status, method, first["message"]["content"]
                # OpenAI legacy choice.text
                if isinstance(first, dict) and "text" in first:
                    return status, method, first["text"]
        except Exception:
            pass

        try:
            if isinstance(llm_result, dict):
                for key in ("text", "result", "output", "content"):
                    if key in llm_result and isinstance(llm_result[key], str):
                        return status, method, llm_result[key]

                for gen_key in ("generations", "generation", "results"):
                    if gen_key in llm_result and isinstance(llm_result[gen_key], (list, tuple)) and len(llm_result[gen_key]) > 0:
                        first_gen = llm_result[gen_key][0]
                        if isinstance(first_gen, dict):
                            # look for common text fields
                            for tkey in ("text", "content", "output", "result"):
                                if tkey in first_gen and isinstance(first_gen[tkey], str):
                                    return status, method, first_gen[tkey]
                        elif isinstance(first_gen, str):
                            return status, method, first_gen
        except Exception:
            pass

        try:
            import json as _json

            pretty = _json.dumps(llm_result)
            return status, method, pretty
        except Exception:
            return status, method, "Whoops! Something went wrong."

    return status, method, "Whoops! Something went wrong."
# endregion