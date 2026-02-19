"""Tests for shaft data schemas and validation."""

import pytest
from pydantic import ValidationError

from src.ingestion.schemas import ClubType, Flex, LaunchProfile, ShaftSpec


class TestShaftSpec:
    def test_valid_shaft(self):
        spec = ShaftSpec(
            manufacturer="Project X",
            model="HZRDUS Black",
            club_type=ClubType.WOODS,
            flex=Flex.STIFF,
            weight_grams=62.0,
            torque_degrees=3.5,
            launch=LaunchProfile.LOW,
        )
        assert spec.manufacturer == "Project X"
        assert spec.weight_grams == 62.0

    def test_display_name(self):
        spec = ShaftSpec(
            manufacturer="Fujikura",
            model="Ventus Blue",
            generation="TR",
            club_type=ClubType.WOODS,
            flex=Flex.X_STIFF,
            weight_grams=67.0,
        )
        assert spec.display_name == "Fujikura Ventus Blue TR X-Stiff"

    def test_display_name_no_generation(self):
        spec = ShaftSpec(
            manufacturer="KBS",
            model="Tour",
            club_type=ClubType.IRON,
            flex=Flex.STIFF,
            weight_grams=120.0,
        )
        assert spec.display_name == "KBS Tour Stiff"

    def test_flex_order(self):
        spec_s = ShaftSpec(
            manufacturer="Test", model="Test", club_type=ClubType.WOODS,
            flex=Flex.STIFF, weight_grams=60.0,
        )
        spec_x = ShaftSpec(
            manufacturer="Test", model="Test", club_type=ClubType.WOODS,
            flex=Flex.X_STIFF, weight_grams=65.0,
        )
        assert spec_s.flex_order < spec_x.flex_order

    def test_invalid_weight_zero(self):
        with pytest.raises(ValidationError):
            ShaftSpec(
                manufacturer="Test", model="Test", club_type=ClubType.WOODS,
                flex=Flex.STIFF, weight_grams=0,
            )

    def test_invalid_weight_negative(self):
        with pytest.raises(ValidationError):
            ShaftSpec(
                manufacturer="Test", model="Test", club_type=ClubType.WOODS,
                flex=Flex.STIFF, weight_grams=-10,
            )

    def test_strips_whitespace(self):
        spec = ShaftSpec(
            manufacturer="  Fujikura  ", model="  Ventus  ",
            club_type=ClubType.WOODS, flex=Flex.STIFF, weight_grams=65.0,
        )
        assert spec.manufacturer == "Fujikura"
        assert spec.model == "Ventus"
