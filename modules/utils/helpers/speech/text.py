"""How far a transcript is from the text it should say: word error rate over normalized words."""

from __future__ import annotations

import re
import unicodedata

_NOT_WORD = re.compile(r"[^\w']+")


def words(text: str) -> list[str]:
    """`text` as lower-case words: Unicode NFKC, curly apostrophes made straight, punctuation dropped."""
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    folded = unicodedata.normalize("NFKC", text).replace("’", "'").replace("‘", "'").lower()
    return [word.strip("'") for word in _NOT_WORD.split(folded) if word.strip("'")]


def word_error_rate(expected: str, heard: str) -> float:
    """Word edits (substitutions, insertions, deletions) turning `expected` into `heard`, per expected word."""
    reference, hypothesis = words(expected), words(heard)
    if not reference:
        raise ValueError("The expected text has no words to compare against.")
    previous = list(range(len(hypothesis) + 1))
    for row, word in enumerate(reference, start=1):
        current = [row]
        for column, other in enumerate(hypothesis, start=1):
            current.append(min(previous[column] + 1, current[column - 1] + 1,
                               previous[column - 1] + (word != other)))
        previous = current
    return round(previous[-1] / len(reference), 4)
