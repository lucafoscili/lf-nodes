from __future__ import annotations

from modules.nodes.logic import extract_prompt_from_lora_tag
from modules.utils.constants import Input


def test_extract_prompt_preserves_published_input_and_output_positions() -> None:
    node = extract_prompt_from_lora_tag.LF_ExtractPromptFromLoraTag
    schema = node.INPUT_TYPES()

    assert tuple(schema["required"]) == ("tag", "separator")
    assert tuple(schema["optional"]) == ("ui_widget",)
    assert tuple(schema["hidden"]) == ("node_id",)
    assert schema["required"]["tag"][0] == Input.STRING
    assert schema["required"]["tag"][1]["multiline"] is True
    assert schema["required"]["separator"][0] == Input.STRING
    assert schema["required"]["separator"][1]["default"] == "SEP"
    assert schema["optional"]["ui_widget"][0] == Input.LF_CODE
    assert schema["hidden"]["node_id"] == "UNIQUE_ID"
    assert not hasattr(node, "INPUT_IS_LIST")
    assert node.RETURN_TYPES == (
        Input.STRING,
        Input.INTEGER,
        Input.STRING,
        Input.INTEGER,
    )
    assert node.RETURN_NAMES == (
        "keywords",
        "keywords_count",
        "keywords_list",
        "keywords_count_list",
    )
    assert node.OUTPUT_IS_LIST == (False, False, True, True)


def test_extract_prompt_returns_aggregate_scalars_and_real_list_outputs(
    monkeypatch,
) -> None:
    events: list[tuple] = []
    monkeypatch.setattr(
        extract_prompt_from_lora_tag,
        "safe_send_sync",
        lambda *args: events.append(args),
    )

    result = extract_prompt_from_lora_tag.LF_ExtractPromptFromLoraTag().on_exec(
        tag=[
            "<lora:firstSEPstyle.safetensors:0.7>",
            (
                "<lora:folder\\secondSEPlook.safetensors:1.0> "
                "<lora:third.safetensors>"
            ),
        ],
        separator=["SEP"],
        node_id=["lora-node"],
    )

    node = extract_prompt_from_lora_tag.LF_ExtractPromptFromLoraTag
    assert node.RETURN_TYPES == (
        Input.STRING,
        Input.INTEGER,
        Input.STRING,
        Input.INTEGER,
    )
    assert node.RETURN_NAMES == (
        "keywords",
        "keywords_count",
        "keywords_list",
        "keywords_count_list",
    )
    assert node.OUTPUT_IS_LIST == (False, False, True, True)
    assert result == (
        "first, style, second, look, third",
        5,
        ["first, style", "second, look", "third"],
        [2, 2, 1],
    )
    assert isinstance(result[0], str)
    assert isinstance(result[1], int)
    assert all(isinstance(value, list) for value in result[2:])
    assert len(events) == 1
    suffix, payload, node_id = events[0]
    assert suffix == "extractpromptfromloratag"
    assert node_id == ["lora-node"]
    assert "first, style" in payload["value"]
    assert "third" in payload["value"]


def test_extract_prompt_keeps_single_tag_scalar_and_list_forms_aligned(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        extract_prompt_from_lora_tag,
        "safe_send_sync",
        lambda *_args: None,
    )

    result = extract_prompt_from_lora_tag.LF_ExtractPromptFromLoraTag().on_exec(
        tag="<lora:soloSEPstyle.safetensors:0.5>",
        separator="SEP",
    )

    assert result == ("solo, style", 2, ["solo, style"], [2])


def test_extract_prompt_uses_singular_defaults_when_no_tag_matches(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        extract_prompt_from_lora_tag,
        "safe_send_sync",
        lambda *_args: None,
    )

    result = extract_prompt_from_lora_tag.LF_ExtractPromptFromLoraTag().on_exec(
        tag="plain prompt without a LoRA tag",
        separator="SEP",
    )

    assert result == ("", 0, [], [])
