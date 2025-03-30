from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple
import string
import random
from pydantic import BaseModel, Field, validator


class ColorMode(Enum):
    """Enumeration of available color modes for the Matrix rain."""

    GREEN = auto()  # Classic Matrix green
    CUSTOM = auto()  # User-defined color
    RAINBOW = auto()  # Rainbow effect where each column has different colors


class CharacterSet(Enum):
    """Enumeration of available character sets for the Matrix rain."""

    LATIN = auto()  # Latin alphabet and numbers
    KATAKANA = auto()  # Japanese Katakana characters
    MIXED = auto()  # Mix of symbols, Latin and Katakana
    BINARY = auto()  # Just 0 and 1
    CUSTOM = auto()  # User-defined character set


class MatrixConfigModel(BaseModel):
    """Pydantic model for validating Matrix configuration."""

    width: int = Field(800, ge=640, le=7680)
    height: int = Field(600, ge=480, le=4320)
    fullscreen: bool = False

    # Rain effect settings
    rain_speed: float = Field(1.0, ge=0.1, le=5.0)
    rain_density: float = Field(1.0, ge=0.1, le=2.0)

    # Character settings
    char_set: CharacterSet = CharacterSet.MIXED
    custom_chars: str = "ABC"
    char_size_min: int = Field(10, ge=6, le=40)
    char_size_max: int = Field(20, ge=6, le=40)

    # Color settings
    color_mode: ColorMode = ColorMode.GREEN
    base_color: Tuple[int, int, int] = (0, 255, 0)  # Default Matrix green
    fading_speed: float = Field(0.07, ge=0.01, le=0.5)

    # Speed variation settings
    speed_variation: float = Field(0.5, ge=0.0, le=2.0)

    @validator("char_size_max")
    def max_size_greater_than_min(cls, v, values):
        if "char_size_min" in values and v < values["char_size_min"]:
            raise ValueError(
                "Maximum character size must be greater than or equal to minimum size"
            )
        return v

    @validator("custom_chars")
    def validate_custom_chars(cls, v, values):
        if "char_set" in values and values["char_set"] == CharacterSet.CUSTOM and not v:
            raise ValueError(
                "Custom character set must not be empty when CharacterSet.CUSTOM is selected"
            )
        return v


@dataclass
class MatrixConfig:
    """
    Configuration class for the Matrix rain animation.

    This class holds all adjustable parameters for the Matrix rain effect
    and provides utility methods for character generation and validation.
    """

    width: int = 800
    height: int = 600
    fullscreen: bool = False

    # Rain effect settings
    rain_speed: float = 1.0
    rain_density: float = 1.0

    # Character settings
    char_set: CharacterSet = CharacterSet.MIXED
    custom_chars: str = ""
    char_size_min: int = 10
    char_size_max: int = 20

    # Color settings
    color_mode: ColorMode = ColorMode.GREEN
    base_color: Tuple[int, int, int] = (0, 255, 0)  # Default Matrix green
    fading_speed: float = 0.07

    # Speed variation settings
    speed_variation: float = 0.5

    # Cached character set
    _cached_chars: List[str] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate the configuration after initialization."""
        self._validate()
        self._update_char_set()

    def _validate(self) -> None:
        """Validate the configuration using Pydantic."""
        try:
            # Create Pydantic model from current values
            MatrixConfigModel(
                width=self.width,
                height=self.height,
                fullscreen=self.fullscreen,
                rain_speed=self.rain_speed,
                rain_density=self.rain_density,
                char_set=self.char_set,
                custom_chars=self.custom_chars,
                char_size_min=self.char_size_min,
                char_size_max=self.char_size_max,
                color_mode=self.color_mode,
                base_color=self.base_color,
                fading_speed=self.fading_speed,
                speed_variation=self.speed_variation,
            )
        except Exception as e:
            # Reset to defaults if validation fails
            self.__init__()
            raise ValueError(f"Configuration validation failed: {e}")

    def _update_char_set(self) -> None:
        """Update the cached character set based on the current configuration."""
        if self.char_set == CharacterSet.LATIN:
            self._cached_chars = list(string.ascii_letters + string.digits)
        elif self.char_set == CharacterSet.KATAKANA:
            # Katakana Unicode range (U+30A0 to U+30FF)
            self._cached_chars = [chr(i) for i in range(0x30A0, 0x30FF + 1)]
        elif self.char_set == CharacterSet.BINARY:
            self._cached_chars = ["0", "1"]
        elif self.char_set == CharacterSet.CUSTOM and self.custom_chars:
            self._cached_chars = list(self.custom_chars)
        else:  # Default to MIXED
            # Latin, digits, and some special characters
            latin_set = list(
                string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
            )
            # Some Katakana characters
            katakana_set = [
                chr(int("0x30a0", 16) + i) for i in range(96)
            ]  # Taking every 4th character to keep the set smaller
            self._cached_chars = latin_set + katakana_set

    def get_random_char(self) -> str:
        """
        Get a random character from the current character set.

        Returns:
            str: A random character
        """
        if not self._cached_chars:
            self._update_char_set()

        return random.choice(self._cached_chars)

    def update(self, **kwargs) -> None:
        """
        Update configuration with new values.

        Args:
            **kwargs: Key-value pairs of configuration parameters to update
        """
        # Update the attributes
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Validate the new configuration
        self._validate()

        # Update character set if needed
        if "char_set" in kwargs or "custom_chars" in kwargs:
            self._update_char_set()
