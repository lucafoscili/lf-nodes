from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.logic import normalize_json_input

# region LF_LLMChat
class LF_LLMChat:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "ui_widget": (Input.LF_CHAT, {
                    "default": ""
                }),
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, False, False, True)
    OUTPUT_TOOLTIPS = (
        "Chat history as JSON.",
        "Last message in the chat.",
        "Last message from the user.",
        "Last message from the LLM.",
        "All messages in the chat."
    )
    RETURN_NAMES = ("chat_history_json", "last_message", "last_user_message", "last_llm_message", "all_messages")
    RETURN_TYPES = (Input.JSON, Input.STRING, Input.STRING, Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        all_messages = [message.get("content") for message in ui_widget]
        last_message = all_messages[-1]
        last_user_message = next((message.get("content") for message in reversed(ui_widget) if message["role"] == "user"), "")
        last_llm_message = next((message.get("content") for message in reversed(ui_widget) if message["role"] == "assistant"), "")

        return (ui_widget, last_message, last_user_message, last_llm_message, all_messages)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LLMChat": LF_LLMChat,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LLMChat": "LLM Chat",
}
# endregion
