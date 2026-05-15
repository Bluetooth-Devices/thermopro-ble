"""Tests for the model registry."""

from __future__ import annotations

import pytest

from thermopro_ble.models import (
    CAP_SET_DATETIME,
    KNOWN_FAMILIES,
    KNOWN_MODELS,
    get_model,
    has_capability,
    is_supported_model,
    models_with_capability,
)


def test_known_models_is_non_empty() -> None:
    assert len(KNOWN_MODELS) > 0


def test_known_families_covers_every_model() -> None:
    for model in KNOWN_MODELS:
        assert model.name.startswith(model.family), (
            f"{model.name} does not start with declared family {model.family}"
        )
    families_from_models = {m.family for m in KNOWN_MODELS}
    assert set(KNOWN_FAMILIES) == families_from_models


def test_known_models_have_unique_names() -> None:
    names = [m.name for m in KNOWN_MODELS]
    assert len(names) == len(set(names))


def test_is_supported_model_accepts_bare_name() -> None:
    assert is_supported_model("TP357S") is True
    assert is_supported_model("TP358") is True


def test_is_supported_model_accepts_advertised_name() -> None:
    assert is_supported_model("TP357S (2142)") is True
    assert is_supported_model("TP972S (ABCD)") is True


def test_is_supported_model_rejects_unknown() -> None:
    assert is_supported_model("TP123") is False
    assert is_supported_model("MI_TS") is False
    assert is_supported_model("") is False


def test_get_model_returns_entry_for_known_name() -> None:
    model = get_model("TP358S (2142)")
    assert model is not None
    assert model.name == "TP358S"
    assert model.family == "TP35"


def test_get_model_returns_none_for_unknown() -> None:
    assert get_model("TP999X") is None


def test_has_capability_true_for_datetime_models() -> None:
    assert has_capability("TP358", CAP_SET_DATETIME) is True
    assert has_capability("TP358S (2142)", CAP_SET_DATETIME) is True


def test_has_capability_false_for_models_without_capability() -> None:
    assert has_capability("TP357", CAP_SET_DATETIME) is False
    assert has_capability("TP972S", CAP_SET_DATETIME) is False


def test_has_capability_false_for_unknown_model() -> None:
    assert has_capability("TP999X", CAP_SET_DATETIME) is False


def test_models_with_capability_returns_expected_set() -> None:
    assert models_with_capability(CAP_SET_DATETIME) == frozenset({"TP358", "TP358S"})


def test_models_with_capability_unknown_capability_returns_empty() -> None:
    assert models_with_capability("does_not_exist") == frozenset()


@pytest.mark.parametrize(
    "name",
    [
        "TP357",
        "TP357S",
        "TP358",
        "TP358S",
        "TP393",
        "TP960R",
        "TP962R",
        "TP970R",
        "TP972",
        "TP972S",
    ],
)
def test_every_documented_model_is_registered(name: str) -> None:
    """Sanity check: models exercised by the parser test fixtures must
    appear in the registry. Test fails loud if a fixture is added without
    updating the registry.
    """
    assert is_supported_model(name)
