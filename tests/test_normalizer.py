"""Tests for shaft data normalization."""

import pytest

from src.ingestion.normalizer import (
    normalize_flex,
    normalize_kickpoint,
    normalize_launch,
    normalize_spin,
)
from src.ingestion.schemas import Flex, Kickpoint, LaunchProfile, SpinProfile


class TestNormalizeFlex:
    def test_standard_flexes(self):
        assert normalize_flex("S") == Flex.STIFF
        assert normalize_flex("R") == Flex.REGULAR
        assert normalize_flex("X") == Flex.X_STIFF
        assert normalize_flex("TX") == Flex.TX
        assert normalize_flex("A") == Flex.SENIOR
        assert normalize_flex("L") == Flex.LADIES

    def test_full_names(self):
        assert normalize_flex("Stiff") == Flex.STIFF
        assert normalize_flex("Regular") == Flex.REGULAR
        assert normalize_flex("Senior") == Flex.SENIOR
        assert normalize_flex("X-Stiff") == Flex.X_STIFF

    def test_case_insensitive(self):
        assert normalize_flex("stiff") == Flex.STIFF
        assert normalize_flex("STIFF") == Flex.STIFF
        assert normalize_flex("x-stiff") == Flex.X_STIFF

    def test_weight_flex_combos(self):
        assert normalize_flex("6.0S") == Flex.STIFF
        assert normalize_flex("60X") == Flex.X_STIFF
        assert normalize_flex("5.5R") == Flex.REGULAR

    def test_invalid_flex(self):
        with pytest.raises(ValueError):
            normalize_flex("banana")


class TestNormalizeLaunch:
    def test_standard_values(self):
        assert normalize_launch("Low") == LaunchProfile.LOW
        assert normalize_launch("Mid") == LaunchProfile.MID
        assert normalize_launch("High") == LaunchProfile.HIGH
        assert normalize_launch("Low-Mid") == LaunchProfile.LOW_MID
        assert normalize_launch("Mid-High") == LaunchProfile.MID_HIGH

    def test_slash_format(self):
        assert normalize_launch("Low/Mid") == LaunchProfile.LOW_MID
        assert normalize_launch("Mid/High") == LaunchProfile.MID_HIGH

    def test_none_handling(self):
        assert normalize_launch(None) is None
        assert normalize_launch("") is None


class TestNormalizeSpin:
    def test_standard_values(self):
        assert normalize_spin("Low") == SpinProfile.LOW
        assert normalize_spin("Mid") == SpinProfile.MID
        assert normalize_spin("High") == SpinProfile.HIGH

    def test_none_handling(self):
        assert normalize_spin(None) is None


class TestNormalizeKickpoint:
    def test_standard_values(self):
        assert normalize_kickpoint("Low") == Kickpoint.LOW
        assert normalize_kickpoint("Mid") == Kickpoint.MID
        assert normalize_kickpoint("High") == Kickpoint.HIGH

    def test_alternative_names(self):
        assert normalize_kickpoint("Front") == Kickpoint.LOW
        assert normalize_kickpoint("Rear") == Kickpoint.HIGH

    def test_none_handling(self):
        assert normalize_kickpoint(None) is None
