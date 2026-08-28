from __future__ import annotations

from pathlib import Path

import pytest

from modules.nodes.io import save_markdown, save_text


@pytest.mark.parametrize(
    ("module", "node_class", "input_name", "content", "extension", "schema", "event"),
    (
        (
            save_text,
            save_text.LF_SaveText,
            "text",
            "plain text\n",
            "txt",
            "lf.text_file.receipt.v1",
            "savetext",
        ),
        (
            save_markdown,
            save_markdown.LF_SaveMarkdown,
            "markdown_text",
            "# Heading\n",
            "md",
            "lf.markdown_file.receipt.v1",
            "savemarkdown",
        ),
    ),
)
def test_text_saver_publishes_restart_safe_artifact_receipt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    module,
    node_class,
    input_name: str,
    content: str,
    extension: str,
    schema: str,
    event: str,
) -> None:
    output_root = tmp_path / "output"
    destination = output_root / "notes" / f"result.{extension}"
    destination.parent.mkdir(parents=True)
    sent = []

    monkeypatch.setattr(module, "get_comfy_dir", lambda kind: str(output_root))
    monkeypatch.setattr(
        module,
        "resolve_filepath",
        lambda **_kwargs: (str(destination), "notes", destination.name),
    )
    monkeypatch.setattr(
        module,
        "safe_send_sync",
        lambda event_name, payload, node_id: sent.append(
            (event_name, payload, node_id)
        ),
    )

    kwargs = {
        input_name: [content],
        "filename_prefix": ["notes/result"],
        "add_timestamp": [False],
        "node_id": ["save-7"],
    }
    if node_class is save_text.LF_SaveText:
        kwargs["add_counter"] = [False]

    response = node_class().on_exec(**kwargs)

    assert destination.read_text(encoding="utf-8") == content
    payload = response["ui"]["lf_output"][0]
    assert response["result"] == (content,)
    assert payload["file_names"] == [f"notes/result.{extension}"]
    assert payload["receipt"] == {
        "schema": schema,
        "file_name": f"notes/result.{extension}",
        "storage_type": "output",
        "byte_length": len(destination.read_bytes()),
    }
    assert sent == [(event, payload, ["save-7"])]


@pytest.mark.parametrize(
    ("module", "node_class", "input_name", "extension"),
    (
        (save_text, save_text.LF_SaveText, "text", "txt"),
        (save_markdown, save_markdown.LF_SaveMarkdown, "markdown_text", "md"),
    ),
)
def test_text_saver_rejects_paths_outside_output_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    module,
    node_class,
    input_name: str,
    extension: str,
) -> None:
    output_root = tmp_path / "output"
    output_root.mkdir()
    escaped = tmp_path / f"escaped.{extension}"
    monkeypatch.setattr(module, "get_comfy_dir", lambda kind: str(output_root))
    monkeypatch.setattr(
        module,
        "resolve_filepath",
        lambda **_kwargs: (str(escaped), "", escaped.name),
    )

    kwargs = {
        input_name: "content",
        "filename_prefix": "result",
        "add_timestamp": False,
    }
    if node_class is save_text.LF_SaveText:
        kwargs["add_counter"] = False

    with pytest.raises(ValueError, match="inside ComfyUI's output directory"):
        node_class().on_exec(**kwargs)

    assert not escaped.exists()
