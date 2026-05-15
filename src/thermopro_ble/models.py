"""Registry of known ThermoPro models.

Centralises model metadata so downstream integrations can introspect what
this library supports without grepping prefix matches out of the parser.
Used by both the advertisement parser (``parser.py``) and the GATT helper
(``device.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# A model "family" is what we route advertisements by; every known model
# starts with one of these prefixes. The parser uses ``KNOWN_FAMILIES`` for
# its top-level filter.
ModelFamily = Literal["TP35", "TP39", "TP96", "TP97", "TP90"]

# How a model exposes sensor data:
#   - "advertisement": data is decoded from BLE manufacturer data (passive)
#   - "gatt": data only flows over a GATT notify characteristic (active)
SensorTransport = Literal["advertisement", "gatt"]


@dataclass(frozen=True)
class ThermoProModel:
    """Metadata describing one ThermoPro model line."""

    name: str
    family: ModelFamily
    transport: SensorTransport
    description: str
    capabilities: frozenset[str] = field(default_factory=frozenset)


# Capability flags. Keep these short and stable — downstream code checks
# them via ``has_capability(name, "set_datetime")``.
CAP_SET_DATETIME = "set_datetime"


# The authoritative list of models this library has been validated against.
# Add a new entry when adding a fixture or wiring a new decoder. Names must
# match the BLE advertised name exactly (without the trailing " (XXXX)"
# address suffix).
KNOWN_MODELS: tuple[ThermoProModel, ...] = (
    ThermoProModel(
        name="TP357",
        family="TP35",
        transport="advertisement",
        description="Indoor temperature & humidity sensor.",
    ),
    ThermoProModel(
        name="TP357S",
        family="TP35",
        transport="advertisement",
        description="Indoor temperature & humidity sensor (revised).",
    ),
    ThermoProModel(
        name="TP358",
        family="TP35",
        transport="advertisement",
        description="Indoor temperature & humidity sensor with clock.",
        capabilities=frozenset({CAP_SET_DATETIME}),
    ),
    ThermoProModel(
        name="TP358S",
        family="TP35",
        transport="advertisement",
        description="Indoor temperature & humidity sensor with clock (revised).",
        capabilities=frozenset({CAP_SET_DATETIME}),
    ),
    ThermoProModel(
        name="TP393",
        family="TP39",
        transport="advertisement",
        description="Indoor temperature & humidity sensor with display.",
    ),
    ThermoProModel(
        name="TP960R",
        family="TP96",
        transport="advertisement",
        description="TempSpike wireless meat probe (single probe).",
    ),
    ThermoProModel(
        name="TP962R",
        family="TP96",
        transport="advertisement",
        description="TempSpike wireless meat probe (dual probe).",
    ),
    ThermoProModel(
        name="TP970R",
        family="TP97",
        transport="advertisement",
        description="TempSpike Plus wireless meat probe.",
    ),
    ThermoProModel(
        name="TP972",
        family="TP97",
        transport="advertisement",
        description="TempSpike Pro wireless meat probe.",
    ),
    ThermoProModel(
        name="TP972S",
        family="TP97",
        transport="advertisement",
        description="TempSpike Pro wireless meat probe (revised).",
    ),
)


# Prefix tuple used by the advertisement parser for its first-pass filter.
# Keep this derived from ``KNOWN_MODELS`` so adding a new model in one place
# is enough to make it routable.
KNOWN_FAMILIES: tuple[str, ...] = tuple(sorted({m.family for m in KNOWN_MODELS}))


_BY_NAME: dict[str, ThermoProModel] = {m.name: m for m in KNOWN_MODELS}


def _split_model(name_or_model: str) -> str:
    """Return the bare model token from an advertised name.

    Advertised names look like ``"TP358S (2142)"``; the address suffix is
    stripped so callers can pass either form.
    """
    return name_or_model.split(" ", 1)[0]


def get_model(name_or_model: str) -> ThermoProModel | None:
    """Return the :class:`ThermoProModel` entry for an advertised name."""
    return _BY_NAME.get(_split_model(name_or_model))


def is_supported_model(name_or_model: str) -> bool:
    """Return True if ``name_or_model`` is in the supported registry."""
    return _split_model(name_or_model) in _BY_NAME


def has_capability(name_or_model: str, capability: str) -> bool:
    """Return True if the model is known and declares ``capability``."""
    model = get_model(name_or_model)
    return model is not None and capability in model.capabilities


def models_with_capability(capability: str) -> frozenset[str]:
    """Return the set of model names declaring ``capability``."""
    return frozenset(m.name for m in KNOWN_MODELS if capability in m.capabilities)


__all__ = [
    "CAP_SET_DATETIME",
    "KNOWN_FAMILIES",
    "KNOWN_MODELS",
    "ModelFamily",
    "SensorTransport",
    "ThermoProModel",
    "get_model",
    "has_capability",
    "is_supported_model",
    "models_with_capability",
]
