"""Data models and validation for golf shaft specifications."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ClubType(str, Enum):
    WOODS = "woods"
    FAIRWAY = "fairway"
    HYBRID = "hybrid"
    IRON = "iron"
    WEDGE = "wedge"
    PUTTER = "putter"


class Flex(str, Enum):
    LADIES = "Ladies"
    SENIOR = "Senior"
    REGULAR = "Regular"
    STIFF = "Stiff"
    X_STIFF = "X-Stiff"
    TX = "TX"


FLEX_ORDER = {
    Flex.LADIES: 0,
    Flex.SENIOR: 1,
    Flex.REGULAR: 2,
    Flex.STIFF: 3,
    Flex.X_STIFF: 4,
    Flex.TX: 5,
}


class LaunchProfile(str, Enum):
    LOW = "Low"
    LOW_MID = "Low-Mid"
    MID = "Mid"
    MID_HIGH = "Mid-High"
    HIGH = "High"


class SpinProfile(str, Enum):
    LOW = "Low"
    LOW_MID = "Low-Mid"
    MID = "Mid"
    MID_HIGH = "Mid-High"
    HIGH = "High"


class TipStiffness(str, Enum):
    SOFT = "Soft"
    MEDIUM = "Medium"
    FIRM = "Firm"
    VERY_FIRM = "Very Firm"


class Kickpoint(str, Enum):
    LOW = "Low"
    LOW_MID = "Low-Mid"
    MID = "Mid"
    MID_HIGH = "Mid-High"
    HIGH = "High"


class ShaftSpec(BaseModel):
    """Normalized golf shaft specification."""

    manufacturer: str = Field(..., min_length=1, description="Shaft OEM name")
    model: str = Field(..., min_length=1, description="Product line name")
    generation: Optional[str] = Field(None, description="Generation or version")
    club_type: ClubType = Field(..., description="Intended club type")
    flex: Flex = Field(..., description="Shaft flex rating")
    weight_grams: float = Field(..., gt=0, lt=300, description="Weight in grams")
    length_inches: Optional[float] = Field(None, gt=0, lt=60, description="Uncut length")
    torque_degrees: Optional[float] = Field(None, ge=0, lt=15, description="Torque in degrees")
    launch: Optional[LaunchProfile] = Field(None, description="Launch profile")
    spin: Optional[SpinProfile] = Field(None, description="Spin profile")
    butt_diameter_inches: Optional[float] = Field(None, description="Butt diameter")
    tip_diameter_inches: Optional[float] = Field(None, description="Tip diameter")
    tip_stiff: Optional[TipStiffness] = Field(None, description="Tip stiffness")
    kickpoint: Optional[Kickpoint] = Field(None, description="Kickpoint location")
    material: str = Field(default="graphite", description="Shaft material")
    msrp_usd: Optional[float] = Field(None, ge=0, description="MSRP in USD")

    @field_validator("manufacturer", "model")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @property
    def flex_order(self) -> int:
        """Numeric flex ordering for sorting."""
        return FLEX_ORDER.get(self.flex, 3)

    @property
    def display_name(self) -> str:
        """Human-readable shaft identifier."""
        gen = f" {self.generation}" if self.generation else ""
        return f"{self.manufacturer} {self.model}{gen} {self.flex.value}"
