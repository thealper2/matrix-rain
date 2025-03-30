import random
import pygame
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

from matrix_config import MatrixConfig, ColorMode


@dataclass
class RainDrop:
    """
    Represents a single character in the Matrix rain.

    Attributes:
        x: X-coordinate position
        y: Y-coordinate position
        char: The character to display
        speed: Falling speed
        color: RGB color tuple
        brightness: Current brightness (0.0-1.0)
        size: Font size
    """

    x: int
    y: float
    char: str
    speed: float
    color: Tuple[int, int, int]
    brightness: float = 1.0
    size: int = 16

    def update(self, config: MatrixConfig) -> None:
        """
        Update the raindrop position and properties.

        Args:
            config: Current matrix configuration
        """
        self.y += self.speed * config.rain_speed

        # Randomly change character (small chance)
        if random.random() < 0.02:
            self.char = config.get_random_char()

        # Dim the brightness as it falls (except for head character)
        if self.brightness > 0.2:
            self.brightness -= 0.01 * config.fading_speed

    def is_offscreen(self, height: int) -> bool:
        """
        Check if the raindrop has moved off-screen.

        Args:
            height: Screen height

        Returns:
            bool: True if off-screen, False otherwise
        """
        return self.y > height


@dataclass
class RainColumn:
    """
    Represents a column of falling characters.

    Attributes:
        x: X-coordinate position
        drops: List of raindrops in this column
        speed: Base falling speed
        length: Maximum number of characters in column
        active: Whether this column is currently active
        next_spawn_time: Time until next character spawn
        color: Base color for this column
        size: Font size for characters in this column
    """

    x: int
    drops: List[RainDrop]
    speed: float
    length: int
    active: bool = True
    next_spawn_time: int = 0
    color: Tuple[int, int, int] = (0, 255, 0)
    size: int = 16

    def update(self, config: MatrixConfig, current_time: int) -> None:
        """
        Update the rain column state.

        Args:
            config: Current matrix configuration
            current_time: Current game time in milliseconds
        """
        # Update existing drops
        for drop in self.drops:
            drop.update(config)

        # Remove off-screen drops
        self.drops = [
            drop for drop in self.drops if not drop.is_offscreen(config.height)
        ]

        # Add new drops if it's time and we're not at max length
        if (
            self.active
            and current_time >= self.next_spawn_time
            and len(self.drops) < self.length
        ):
            # Create a new drop at the top with full brightness
            new_char = config.get_random_char()

            # Determine color based on mode
            if config.color_mode == ColorMode.RAINBOW:
                # Generate a rainbow color
                hue = (current_time / 10000 + self.x / 50) % 1.0
                self.color = self._hsv_to_rgb(hue, 1.0, 1.0)
            elif config.color_mode == ColorMode.CUSTOM:
                self.color = config.base_color

            new_drop = RainDrop(
                x=self.x,
                y=0,
                char=new_char,
                speed=self.speed,
                color=self.color,
                brightness=1.0,
                size=self.size,
            )

            self.drops.append(new_drop)

            # Set the next spawn time with some randomness
            spawn_delay = int(50 / config.rain_density * (random.random() * 0.5 + 0.75))
            self.next_spawn_time = current_time + spawn_delay

        # Small chance to deactivate a column
        if random.random() < 0.001:
            self.active = False

        # Small chance to reactivate a column if it's inactive
        if not self.active and random.random() < 0.05:
            self.active = True
            self.next_spawn_time = current_time + random.randint(0, 1000)

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """
        Convert HSV color to RGB.

        Args:
            h: Hue (0-1)
            s: Saturation (0-1)
            v: Value (0-1)

        Returns:
            Tuple of (r, g, b) values (0-255)
        """
        if s == 0.0:
            return int(v * 255), int(v * 255), int(v * 255)

        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))

        i %= 6

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return int(r * 255), int(g * 255), int(b * 255)


class MatrixRenderer:
    """
    Renderer for the Matrix rain effect.

    This class manages the creation, updating, and rendering of the Matrix rain columns.
    """

    def __init__(self, config: MatrixConfig):
        """
        Initialize the Matrix renderer.

        Args:
            config: Matrix configuration
        """
        self.config = config
        self.columns: List[RainColumn] = []
        self.fonts: Dict[int, pygame.font.Font] = {}
        self.trails_surface: Optional[pygame.Surface] = None
        self.last_time = pygame.time.get_ticks()

        # Initialize the renderer
        self.resize(config)

    def resize(self, config: MatrixConfig) -> None:
        """
        Resize the renderer based on configuration.

        Args:
            config: Updated matrix configuration
        """
        self.config = config

        # Create the trails surface for fade effect
        self.trails_surface = pygame.Surface(
            (config.width, config.height), pygame.SRCALPHA
        )
        self.trails_surface.fill((0, 0, 0))

        # Reset columns
        self.reset_matrix()

        # Preload fonts
        self._preload_fonts()

    def reset_matrix(self) -> None:
        """Reset the Matrix rain columns."""
        # Clear existing columns
        self.columns = []

        # Calculate spacing and create columns
        spacing = max(10, self.config.char_size_max + 2)
        num_columns = self.config.width // spacing

        for i in range(num_columns):
            x_pos = i * spacing + random.randint(-3, 3)

            # Randomize column properties
            column_speed = 1.0 + random.uniform(
                -self.config.speed_variation, self.config.speed_variation
            )
            column_length = random.randint(5, 30)

            # Randomize character size within range
            char_size = random.randint(
                self.config.char_size_min, self.config.char_size_max
            )

            # Create a new column
            column = RainColumn(
                x=x_pos,
                drops=[],
                speed=column_speed,
                length=column_length,
                active=random.random() > 0.2,  # 80% chance to start active
                next_spawn_time=random.randint(0, 2000),  # Random initial delay
                color=self.config.base_color,
                size=char_size,
            )

            self.columns.append(column)

    def _preload_fonts(self) -> None:
        """Preload fonts of different sizes for efficiency."""
        self.fonts = {}

        try:
            min_size = self.config.char_size_min
            max_size = self.config.char_size_max

            for size in range(min_size, max_size + 1, 2):
                try:
                    self.fonts[size] = pygame.font.Font(None, size)
                except pygame.error:
                    # Fall back to default if specific size fails
                    self.fonts[size] = pygame.font.SysFont("monospace", size)
        except Exception as e:
            print(f"Warning: Font loading error: {e}")
            # Fallback to system font
            default_size = (self.config.char_size_min + self.config.char_size_max) // 2
            self.fonts[default_size] = pygame.font.SysFont("monospace", default_size)

    def update(self) -> None:
        """Update the state of all Matrix rain elements."""
        current_time = pygame.time.get_ticks()
        time_delta = current_time - self.last_time
        self.last_time = current_time

        # Skip update if too much time passed (e.g., window was inactive)
        if time_delta > 500:
            return

        # Update all columns
        for column in self.columns:
            column.update(self.config, current_time)

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the Matrix rain effect.

        Args:
            surface: Surface to render onto
        """
        # Clear the screen
        surface.fill((0, 0, 0))

        # Apply fade effect to the trails surface
        self.trails_surface.fill(
            (0, 0, 0, int(255 * self.config.fading_speed)),
            special_flags=pygame.BLEND_RGBA_MULT,
        )

        # Render each column
        for column in self.columns:
            self._render_column(column, surface)

        # Blend the trails with the main surface
        surface.blit(self.trails_surface, (0, 0), special_flags=pygame.BLEND_ADD)

    def _render_column(self, column: RainColumn, surface: pygame.Surface) -> None:
        """
        Render a single Matrix rain column.

        Args:
            column: The rain column to render
            surface: Surface to render onto
        """
        # Get the appropriate font
        font = self._get_font(column.size)

        # Render each drop in the column
        for i, drop in enumerate(column.drops):
            # Calculate color based on brightness
            if i == 0 and column.active:  # Head character (always bright)
                # The head character is white or very bright
                color = (255, 255, 255)
            else:
                # Adjust color based on brightness
                r = min(255, int(drop.color[0] * drop.brightness))
                g = min(255, int(drop.color[1] * drop.brightness))
                b = min(255, int(drop.color[2] * drop.brightness))
                color = (r, g, b)

            # Render the character
            try:
                text = font.render(drop.char, True, color)
                surface.blit(text, (drop.x, int(drop.y)))

                # Add to trails surface with reduced alpha
                alpha_text = font.render(
                    drop.char, True, (*color, int(150 * drop.brightness))
                )
                self.trails_surface.blit(alpha_text, (drop.x, int(drop.y)))
            except Exception as e:
                # Skip rendering this character if it fails
                continue

    def _get_font(self, size: int) -> pygame.font.Font:
        """
        Get a font of the specified size.

        Args:
            size: Font size

        Returns:
            pygame.font.Font: Font object
        """
        # Use closest available font size
        if size not in self.fonts:
            # Find closest available size
            sizes = list(self.fonts.keys())
            closest_size = min(sizes, key=lambda x: abs(x - size))
            return self.fonts[closest_size]

        return self.fonts[size]
