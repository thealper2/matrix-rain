import pygame
from typing import Tuple, Any, List, Callable
from abc import ABC, abstractmethod

from matrix_config import MatrixConfig, ColorMode, CharacterSet


class UIElement(ABC):
    """Abstract base class for UI elements."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the UI element on the surface."""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.

        Returns:
            bool: True if the event was handled, False otherwise
        """
        pass


class Button(UIElement):
    """A simple button UI element."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Callable[[], None],
    ):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button."""
        # Draw button background
        color = (100, 100, 100)
        if self.hovered:
            color = (150, 150, 150)
        if self.active:
            color = (200, 200, 200)

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)

        # Draw text
        try:
            font = pygame.font.SysFont(None, 24)
            text_surf = font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
        except Exception as e:
            print(f"Warning: Button text rendering error: {e}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle button events."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active:
                self.active = False
                if self.rect.collidepoint(event.pos):
                    self.callback()
                return True

        return False


class Slider(UIElement):
    """A slider control for adjusting numeric values."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_val: float,
        max_val: float,
        initial_val: float,
        label: str,
        callback: Callable[[float], None],
    ):
        super().__init__(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.callback = callback
        self.dragging = False

        # Calculate normalized position
        self.handle_pos = int(
            (self.value - self.min_val) / (self.max_val - self.min_val) * width
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the slider."""
        # Draw track
        track_rect = pygame.Rect(
            self.rect.x, self.rect.y + self.rect.height // 2 - 2, self.rect.width, 4
        )
        pygame.draw.rect(surface, (100, 100, 100), track_rect)

        # Draw handle
        handle_rect = pygame.Rect(
            self.rect.x + self.handle_pos - 5, self.rect.y, 10, self.rect.height
        )
        color = (150, 150, 150)
        if self.active:
            color = (200, 200, 200)
        pygame.draw.rect(surface, color, handle_rect)

        # Draw label and value
        try:
            font = pygame.font.SysFont(None, 20)
            label_text = f"{self.label}: {self.value:.2f}"
            text_surf = font.render(label_text, True, (200, 200, 200))
            text_rect = text_surf.get_rect(midleft=(self.rect.x, self.rect.y - 10))
            surface.blit(text_surf, text_rect)
        except Exception as e:
            print(f"Warning: Slider text rendering error: {e}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle slider events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_rect = pygame.Rect(
                self.rect.x + self.handle_pos - 5, self.rect.y, 10, self.rect.height
            )
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
                self.active = True
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                self.active = False
                return True

        if event.type == pygame.MOUSEMOTION and self.dragging:
            # Update handle position
            rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
            self.handle_pos = rel_x

            # Calculate new value
            self.value = self.min_val + (self.max_val - self.min_val) * (
                rel_x / self.rect.width
            )
            self.value = round(self.value * 100) / 100  # Round to 2 decimal places

            # Call the callback
            self.callback(self.value)
            return True

        return False


class Dropdown(UIElement):
    """A dropdown menu for selecting from a list of options."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        options: List[Tuple[Any, str]],
        initial_value: Any,
        label: str,
        callback: Callable[[Any], None],
    ):
        super().__init__(x, y, width, height)
        self.options = options
        self.value = initial_value
        self.label = label
        self.callback = callback
        self.expanded = False

        # Find display text for initial value
        self.display_text = next(
            (text for val, text in options if val == initial_value), ""
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the dropdown."""
        # Draw main button
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)

        # Draw label
        try:
            font = pygame.font.SysFont(None, 20)
            label_surf = font.render(f"{self.label}:", True, (200, 200, 200))
            label_rect = label_surf.get_rect(midleft=(self.rect.x, self.rect.y - 10))
            surface.blit(label_surf, label_rect)

            # Draw selected option
            text_surf = font.render(self.display_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(
                midleft=(self.rect.x + 10, self.rect.y + self.rect.height // 2)
            )
            surface.blit(text_surf, text_rect)

            # Draw dropdown arrow
            arrow_points = [
                (self.rect.right - 15, self.rect.y + self.rect.height // 3),
                (self.rect.right - 5, self.rect.y + self.rect.height // 3),
                (self.rect.right - 10, self.rect.y + 2 * self.rect.height // 3),
            ]
            pygame.draw.polygon(surface, (255, 255, 255), arrow_points)

            # Draw dropdown list if expanded
            if self.expanded:
                list_height = len(self.options) * self.rect.height
                list_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height,
                    self.rect.width,
                    list_height,
                )
                pygame.draw.rect(surface, (50, 50, 50), list_rect)
                pygame.draw.rect(surface, (200, 200, 200), list_rect, 2)

                for i, (_, option_text) in enumerate(self.options):
                    option_rect = pygame.Rect(
                        list_rect.x,
                        list_rect.y + i * self.rect.height,
                        list_rect.width,
                        self.rect.height,
                    )

                    # Highlight option under mouse
                    mouse_pos = pygame.mouse.get_pos()
                    if option_rect.collidepoint(mouse_pos):
                        pygame.draw.rect(surface, (100, 100, 100), option_rect)

                    # Draw option text
                    text_surf = font.render(option_text, True, (255, 255, 255))
                    text_rect = text_surf.get_rect(
                        midleft=(
                            option_rect.x + 10,
                            option_rect.y + option_rect.height // 2,
                        )
                    )
                    surface.blit(text_surf, text_rect)
        except Exception as e:
            print(f"Warning: Dropdown text rendering error: {e}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle dropdown events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True

            if self.expanded:
                list_height = len(self.options) * self.rect.height
                list_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height,
                    self.rect.width,
                    list_height,
                )

                if list_rect.collidepoint(event.pos):
                    # Calculate which option was clicked
                    option_index = (event.pos[1] - list_rect.y) // self.rect.height
                    if 0 <= option_index < len(self.options):
                        self.value, self.display_text = self.options[option_index]
                        self.callback(self.value)
                        self.expanded = False
                        return True

            # Click outside the dropdown, close it
            if self.expanded:
                self.expanded = False
                return True

        return False


class ColorPicker(UIElement):
    """A simple color picker UI element."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        initial_color: Tuple[int, int, int],
        label: str,
        callback: Callable[[Tuple[int, int, int]], None],
    ):
        super().__init__(x, y, width, height)
        self.color = initial_color
        self.label = label
        self.callback = callback
        self.expanded = False

        # Define color swatches
        self.swatches = [
            (0, 255, 0),  # Matrix green
            (0, 255, 255),  # Cyan
            (255, 0, 0),  # Red
            (255, 0, 255),  # Magenta
            (255, 255, 0),  # Yellow
            (255, 255, 255),  # White
            (0, 0, 255),  # Blue
            (128, 0, 255),  # Purple
            (255, 128, 0),  # Orange
        ]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the color picker."""
        # Draw main color box
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)

        # Draw label
        try:
            font = pygame.font.SysFont(None, 20)
            label_surf = font.render(f"{self.label}", True, (200, 200, 200))
            label_rect = label_surf.get_rect(midleft=(self.rect.x, self.rect.y - 10))
            surface.blit(label_surf, label_rect)

            # Draw RGB values
            text = f"RGB: {self.color[0]}, {self.color[1]}, {self.color[2]}"
            text_surf = font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(
                midleft=(
                    self.rect.x + self.rect.width + 10,
                    self.rect.y + self.rect.height // 2,
                )
            )
            surface.blit(text_surf, text_rect)

            # Draw dropdown if expanded
            if self.expanded:
                swatches_per_row = 3
                swatch_size = 30
                padding = 5

                rows = (len(self.swatches) + swatches_per_row - 1) // swatches_per_row
                palette_width = swatches_per_row * (swatch_size + padding) - padding
                palette_height = rows * (swatch_size + padding) - padding

                palette_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height + 5,
                    palette_width,
                    palette_height,
                )
                pygame.draw.rect(surface, (50, 50, 50), palette_rect)
                pygame.draw.rect(surface, (200, 200, 200), palette_rect, 2)

                for i, color in enumerate(self.swatches):
                    row = i // swatches_per_row
                    col = i % swatches_per_row

                    swatch_rect = pygame.Rect(
                        palette_rect.x + col * (swatch_size + padding),
                        palette_rect.y + row * (swatch_size + padding),
                        swatch_size,
                        swatch_size,
                    )

                    pygame.draw.rect(surface, color, swatch_rect)
                    pygame.draw.rect(surface, (200, 200, 200), swatch_rect, 1)
        except Exception as e:
            print(f"Warning: ColorPicker text rendering error: {e}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle color picker events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True

            if self.expanded:
                swatches_per_row = 3
                swatch_size = 30
                padding = 5

                for i, color in enumerate(self.swatches):
                    row = i // swatches_per_row
                    col = i % swatches_per_row

                    swatch_rect = pygame.Rect(
                        self.rect.x + col * (swatch_size + padding),
                        self.rect.y
                        + self.rect.height
                        + 5
                        + row * (swatch_size + padding),
                        swatch_size,
                        swatch_size,
                    )

                    if swatch_rect.collidepoint(event.pos):
                        self.color = color
                        self.callback(color)
                        self.expanded = False
                        return True

                # Click outside the swatches, close the palette
                self.expanded = False
                return True

        return False


class UIControls:
    """Manager class for all UI controls in the Matrix animation."""

    def __init__(self, config: MatrixConfig, screen_width: int, screen_height: int):
        """
        Initialize the UI controls.

        Args:
            config: The matrix configuration
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        self.config = config
        self.elements: List[UIElement] = []
        self.visible = True
        self.toggle_button = None

        # Initialize UI elements
        self._init_ui(screen_width, screen_height)

    def _init_ui(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize UI elements.

        Args:
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        # Clear existing elements
        self.elements = []

        # Panel dimensions
        panel_width = 300
        panel_height = screen_height
        panel_x = screen_width - panel_width
        y_offset = 50
        element_height = 30

        # Create toggle button for UI visibility
        self.toggle_button = Button(
            screen_width - 50, 10, 40, 30, "UI", self._toggle_visibility
        )

        # Add sliders for numeric parameters
        self.elements.append(
            Slider(
                panel_x + 20,
                y_offset,
                panel_width - 40,
                element_height,
                0.1,
                5.0,
                self.config.rain_speed,
                "Rain Speed",
                lambda val: self._update_config(rain_speed=val),
            )
        )

        y_offset += 40
        self.elements.append(
            Slider(
                panel_x + 20,
                y_offset,
                panel_width - 40,
                element_height,
                0.1,
                2.0,
                self.config.rain_density,
                "Rain Density",
                lambda val: self._update_config(rain_density=val),
            )
        )

        y_offset += 40
        self.elements.append(
            Slider(
                panel_x + 20,
                y_offset,
                panel_width - 40,
                element_height,
                6,
                40,
                self.config.char_size_min,
                "Min Char Size",
                lambda val: self._update_config(char_size_min=int(val)),
            )
        )

        y_offset += 40
        self.elements.append(
            Slider(
                panel_x + 20,
                y_offset,
                panel_width - 40,
                element_height,
                6,
                40,
                self.config.char_size_max,
                "Max Char Size",
                lambda val: self._update_config(char_size_max=int(val)),
            )
        )

        y_offset += 40
        self.elements.append(
            Slider(
                panel_x + 20,
                y_offset,
                panel_width - 40,
                element_height,
                0.01,
                0.5,
                self.config.fading_speed,
                "Fade Speed",
                lambda val: self._update_config(fading_speed=val),
            )
        )

        y_offset += 40
        self.elements.append(
            Slider(
                panel_x + 20,
                y_offset,
                panel_width - 40,
                element_height,
                0.0,
                2.0,
                self.config.speed_variation,
                "Speed Variation",
                lambda val: self._update_config(speed_variation=val),
            )
        )

        # Add dropdowns
        y_offset += 60
        self.elements.append(
            Dropdown(
                panel_x + 20,
                y_offset,
                panel_width - 40,
                element_height,
                [
                    (ColorMode.GREEN, "Green"),
                    (ColorMode.CUSTOM, "Custom"),
                    (ColorMode.RAINBOW, "Rainbow"),
                ],
                self.config.color_mode,
                "Color Mode",
                lambda val: self._update_config(color_mode=val),
            )
        )

        y_offset += 60
        self.elements.append(
            Dropdown(
                panel_x + 20,
                y_offset,
                panel_width - 40,
                element_height,
                [
                    (CharacterSet.MIXED, "Mixed"),
                    (CharacterSet.LATIN, "Latin"),
                    (CharacterSet.KATAKANA, "Katakana"),
                    (CharacterSet.BINARY, "Binary"),
                    (CharacterSet.CUSTOM, "Custom"),
                ],
                self.config.char_set,
                "Character Set",
                lambda val: self._update_config(char_set=val),
            )
        )

        # Add color picker
        y_offset += 60
        self.elements.append(
            ColorPicker(
                panel_x + 20,
                y_offset,
                40,
                element_height,
                self.config.base_color,
                "Base Color",
                lambda val: self._update_config(base_color=val),
            )
        )

        # Add reset button
        y_offset += 60
        self.elements.append(
            Button(
                panel_x + panel_width // 2 - 50,
                y_offset,
                100,
                element_height,
                "Reset",
                self._reset_config,
            )
        )

    def resize(self, screen_width: int, screen_height: int) -> None:
        """
        Resize the UI elements.

        Args:
            screen_width: New screen width
            screen_height: New screen height
        """
        self._init_ui(screen_width, screen_height)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw all UI elements.

        Args:
            surface: Surface to draw on
        """
        # Always draw the toggle button
        self.toggle_button.draw(surface)

        if not self.visible:
            return

        # Draw semi-transparent background for UI panel
        panel_rect = pygame.Rect(
            surface.get_width() - 300, 0, 300, surface.get_height()
        )
        panel_surface = pygame.Surface(
            (panel_rect.width, panel_rect.height), pygame.SRCALPHA
        )
        panel_surface.fill((0, 0, 0, 180))
        surface.blit(panel_surface, panel_rect)

        # Draw all UI elements
        for element in self.elements:
            element.draw(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle events for all UI elements.

        Args:
            event: Pygame event

        Returns:
            bool: True if config was updated, False otherwise
        """
        # Always check the toggle button
        if self.toggle_button.handle_event(event):
            return False

        if not self.visible:
            return False

        # Check all other elements
        for element in self.elements:
            if element.handle_event(event):
                return True

        return False

    def _toggle_visibility(self) -> None:
        """Toggle the visibility of the UI panel."""
        self.visible = not self.visible

    def _update_config(self, **kwargs) -> None:
        """
        Update the configuration with new values.

        Args:
            **kwargs: Configuration parameters to update
        """
        self.config.update(**kwargs)

    def _reset_config(self) -> None:
        """Reset the configuration to defaults."""
        # Create a new default configuration
        default_config = MatrixConfig()

        # Update all values except window size/mode
        self.config.update(
            rain_speed=default_config.rain_speed,
            rain_density=default_config.rain_density,
            char_set=default_config.char_set,
            custom_chars=default_config.custom_chars,
            char_size_min=default_config.char_size_min,
            char_size_max=default_config.char_size_max,
            color_mode=default_config.color_mode,
            base_color=default_config.base_color,
            fading_speed=default_config.fading_speed,
            speed_variation=default_config.speed_variation,
        )

        # Update UI elements to reflect new values
        for element in self.elements:
            if isinstance(element, Slider):
                if element.label == "Rain Speed":
                    element.value = default_config.rain_speed
                    element.handle_pos = int(
                        (element.value - element.min_val)
                        / (element.max_val - element.min_val)
                        * element.rect.width
                    )
                elif element.label == "Rain Density":
                    element.value = default_config.rain_density
                    element.handle_pos = int(
                        (element.value - element.min_val)
                        / (element.max_val - element.min_val)
                        * element.rect.width
                    )
                elif element.label == "Min Char Size":
                    element.value = default_config.char_size_min
                    element.handle_pos = int(
                        (element.value - element.min_val)
                        / (element.max_val - element.min_val)
                        * element.rect.width
                    )
                elif element.label == "Max Char Size":
                    element.value = default_config.char_size_max
                    element.handle_pos = int(
                        (element.value - element.min_val)
                        / (element.max_val - element.min_val)
                        * element.rect.width
                    )
                elif element.label == "Fade Speed":
                    element.value = default_config.fading_speed
                    element.handle_pos = int(
                        (element.value - element.min_val)
                        / (element.max_val - element.min_val)
                        * element.rect.width
                    )
                elif element.label == "Speed Variation":
                    element.value = default_config.speed_variation
                    element.handle_pos = int(
                        (element.value - element.min_val)
                        / (element.max_val - element.min_val)
                        * element.rect.width
                    )
            elif isinstance(element, Dropdown):
                if element.label == "Color Mode":
                    element.value = default_config.color_mode
                    element.display_text = next(
                        (text for val, text in element.options if val == element.value),
                        "",
                    )
                elif element.label == "Character Set":
                    element.value = default_config.char_set
                    element.display_text = next(
                        (text for val, text in element.options if val == element.value),
                        "",
                    )
            elif isinstance(element, ColorPicker):
                element.color = default_config.base_color
