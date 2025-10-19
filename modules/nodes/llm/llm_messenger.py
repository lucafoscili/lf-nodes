import json

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.logic import normalize_json_input

# region LF_LLMMessenger
class LF_LLMMessenger:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "ui_widget": (Input.LF_MESSENGER, {
                    "default": ""
                }),
            },
            "optional": {
                "dataset": (Input.JSON, {
                    "default": "",
                    "tooltip": "The dataset JSON containing characters to talk to."
                }),
                "config": (Input.JSON, {
                    "default": "",
                    "tooltip": "Set of parameters that initializes the interface."
                }),
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Chat history as JSON.",
        "Chat history as a string.",
        "Last message in the chat.",
        "Last message from the user.",
        "Last message from the LLM.",
        "Styled prompt for the chat.",
        "Character name.",
        "Outfit name.",
        "Location name.",
        "Style name.",
        "Timeframe name."
    )
    RETURN_NAMES = (
        "chat_history_json", "chat_history_string",
        "last_message", "last_user_message", "last_llm_message", "styled_prompt",
        "character_name", "outfit_name", "location_name", "style_name", "timeframe_name"
    )
    RETURN_TYPES = (
        Input.JSON, Input.STRING, Input.STRING, Input.STRING, Input.STRING, Input.STRING,
        Input.STRING, Input.STRING, Input.STRING, Input.STRING, Input.STRING
    )

    def on_exec(self, **kwargs: dict):
        # Helper functions
        def find_node_by_id(dataset: dict, target_id: str):
            return next((node for node in dataset if isinstance(node, dict) and node.get('id') == target_id), None)

        def get_value_and_description(node: dict):
            """Returns the 'value' and 'description' fields from the node for styled prompt usage."""
            return node.get("value", "No data"), node.get("description", "")

        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))
        dataset: dict = ui_widget.get("dataset", {})
        config: dict = ui_widget.get("config", {})

        if not dataset or not config:
            raise ValueError("It looks like the chat is empty!")
        if "currentCharacter" not in config:
            raise ValueError("You must choose a character")

        # Character data
        character_data: dict = find_node_by_id(dataset.get("nodes"), config.get("currentCharacter"))
        if not character_data:
            raise ValueError(f"Character with id {config['currentCharacter']} not found in dataset")
        character_name: str = character_data.get("value")

        # Process chat data
        try:
            chat_node: dict = find_node_by_id(character_data.get("children"), "chat")
            chat_data: list[dict] = chat_node.get("cells")["lfChat"]["value"]
        except (json.JSONDecodeError, KeyError):
            raise ValueError(f"It looks like the chat with {character_name} is empty")

        all_messages = [message.get("content") for message in chat_data]
        last_message = all_messages[-1] if all_messages else ""
        last_user_message = next((msg.get("content") for msg in reversed(chat_data) if msg["role"] == "user"), "")
        last_llm_message = next((msg.get("content") for msg in reversed(chat_data) if msg["role"] == "assistant"), "")

        # Chat history
        chat_history_string = "\n".join(
            f"User: \"{msg['content']}\"" if msg["role"] == "user" else f"{character_name}: \"{msg['content']}\""
            for msg in chat_data
        )

        # Retrieve additional character settings (style, location, etc.)
        attributes: list[str] = ["styles", "locations", "outfits", "timeframes"]
        settings: dict = {}
        descriptions: dict = {}  # Separate dictionary for styled prompt descriptions

        for attr in attributes:
            node: dict = find_node_by_id(character_data.get("children"), attr)
            if node:
                children = node.get("children")
                index = node.get("value")
                if isinstance(index, int) and isinstance(children, list) and len(children) > 0:
                    value, description = get_value_and_description(children[index])
                    settings[attr[:-1]] = value  # Only 'value' for return
                    descriptions[attr[:-1]] = f"{value}, {description}" if description else value  # 'value, description' for styled prompt

        # Construct the styled prompt
        styled_prompt: str = (
            f"Envision the scene described below from the viewer's point of view.\n"
            f"{character_name} said to the viewer:\n\"{last_llm_message}\"\n"
            + (f"Style of the image: {descriptions['style']}\n" if descriptions.get("style") else "")
            + (f"{character_name}'s outfit: {descriptions['outfit']}\n" if descriptions.get("outfit") else "")
            + (f"Location: {descriptions['location']}\n" if descriptions.get("location") else "")
            + (f"Timeframe: {descriptions['timeframe']}\n" if descriptions.get("timeframe") else "")
            if last_llm_message else None
        )

        # Return values with only names (no descriptions)
        return (
            chat_data, chat_history_string, last_message, last_user_message,
            last_llm_message, styled_prompt, character_name, settings.get("outfit"),
            settings.get("location"), settings.get("style"), settings.get("timeframe")
        )
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LLMMessenger": LF_LLMMessenger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LLMMessenger": "LLM Messenger",
}
# endregion
