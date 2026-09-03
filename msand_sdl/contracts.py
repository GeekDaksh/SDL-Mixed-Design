"""Shared contract types crossing stage boundaries.

Types used by two or more stages live here. Types private to one stage live in
that stage's own contract.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Domain(Enum):
    """Grade domain — decides which IS 10262 route applies. Build_Manual_v3.md §1."""

    NOMINAL = "A"
    ORDINARY = "B"
    HIGH_STRENGTH = "C"


class UseClass(Enum):
    """Structural use. Three values, not two. IS 456 cl 6.1.2 and cl 6.1.3."""

    RCC = "rcc"
    PCC = "pcc"
    LEAN_SIMPLE_TEMPORARY = "cl_6_1_3"


class Exposure(Enum):
    """Exposure class. IS 456 Table 5."""

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"
    EXTREME = "extreme"


class Provenance(Enum):
    """How a value entered the system. Never silently filled."""

    DERIVED_FROM_STANDARD = "derived_from_standard"
    STANDARD_DEFAULT = "standard_default"
    ENGINEER_INPUT = "engineer_input"
    MATERIAL_SPECIFIC = "material_specific"
    PLANT_SPECIFIC = "plant_specific"
    EXPERIMENTALLY_DETERMINED = "experimentally_determined"
    ASSUMED = "assumed"


@dataclass(frozen=True)
class Requirement:
    """What a customer asks for. Input to S04 and S11."""

    # TODO(contracts): fields per Build_Manual_v3.md §2


@dataclass(frozen=True)
class Prediction:
    """A model output. Never a bare float — a prediction carries its uncertainty."""

    # TODO(contracts): mean, sd, interval bounds
