"""Tests for the model registry."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from thermopro_ble.models import (
    CAP_SET_DATETIME,
    KNOWN_FAMILIES,
    KNOWN_MODELS,
    ThermoProModel,
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
    assert has_capability("TP970R", CAP_SET_DATETIME) is False


def test_has_capability_false_for_unknown_model() -> None:
    assert has_capability("TP999X", CAP_SET_DATETIME) is False


def test_models_with_capability_returns_expected_set() -> None:
    assert models_with_capability(CAP_SET_DATETIME) == frozenset({"TP358", "TP358S"})


def test_models_with_capability_unknown_capability_returns_empty() -> None:
    assert models_with_capability("does_not_exist") == frozenset()


def _fixture_model_names() -> frozenset[str]:
    """Extract every ``name="TPxxx ..."`` literal from ``tests/test_parser.py``.

    Walks the AST to find keyword arguments named ``name`` whose value is a
    string literal starting with ``TP`` — i.e. fixture model names passed
    to ``BluetoothServiceInfo``. Names with an address suffix
    (``"TP357 (2142)"``) are split to keep just the bare model token. This
    keeps the registry/fixture coverage check decoupled from any hardcoded
    list in this file.
    """
    parser_tests = Path(__file__).parent / "test_parser.py"
    tree = ast.parse(parser_tests.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.keyword) or node.arg != "name":
            continue
        if not isinstance(node.value, ast.Constant) or not isinstance(
            node.value.value, str
        ):
            continue
        token = node.value.value.split(" ", 1)[0]
        if token.startswith("TP"):
            names.add(token)
    return frozenset(names)


@pytest.mark.parametrize("model", KNOWN_MODELS, ids=lambda m: m.name)
def test_every_model_is_documented_in_readme(model: ThermoProModel) -> None:
    """Every registered model must appear in the README support table so
    docs cannot silently drift from the registry.
    """
    readme = Path(__file__).resolve().parents[1] / "README.md"
    text = readme.read_text()
    # Table rows look like ``| TP357  | TP35 | ...``; require the name to be
    # followed by whitespace so e.g. ``TP357`` doesn't match ``TP357S``.
    assert f"| {model.name} " in text or f"| {model.name}\t" in text, (
        f"{model.name} missing from README support table"
    )


@pytest.mark.parametrize("name", sorted(_fixture_model_names()))
def test_every_fixture_model_is_registered_or_known_negative(name: str) -> None:
    """Every ``TPxxx`` fixture in ``test_parser.py`` must either be in the
    registry, or be one of the deliberate negative-test names that exercise
    the unknown-model path.
    """
    # Negative fixtures used by parser tests to probe the unknown-model
    # rejection path. These are not real models and must not be in the
    # registry.
    NEGATIVE_FIXTURES = {"TP9000NOTHING"}
    if name in NEGATIVE_FIXTURES:
        assert not is_supported_model(name)
    else:
        assert is_supported_model(name), (
            f"{name} is used as a parser fixture but missing from KNOWN_MODELS"
        )
