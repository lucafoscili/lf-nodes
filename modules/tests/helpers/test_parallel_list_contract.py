from __future__ import annotations

import pytest

from modules.utils.helpers.logic import normalize_parallel_list


def test_parallel_list_accepts_exact_values_and_singleton_broadcast() -> None:
    assert normalize_parallel_list([1, 2, 3], 3, "control") == [1, 2, 3]
    assert normalize_parallel_list([7], 3, "control") == [7, 7, 7]
    assert normalize_parallel_list(9, 2, "control") == [9, 9]


def test_parallel_list_rejects_partial_cardinality() -> None:
    with pytest.raises(
        ValueError,
        match="one value to broadcast or exactly 3 values; got 2",
    ):
        normalize_parallel_list([1, 2], 3, "control")
