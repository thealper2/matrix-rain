import sys
import pygame

from matrix_config import MatrixConfig
from matrix_renderer import MatrixRenderer
from ui_controls import UIControls
from error_handler import setup_error_handling, handle_error


def main() -> int:
    """
    Initialize and run the Matrix rain animation.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        # Set up error handling
        setup_error_handling()

        # Initialize Pygame
        pygame.init()

        # Get display info for setting up the window
        display_info = pygame.display.Info()
        screen_width = display_info.current_w
        screen_height = display_info.current_h

        # Create a default configuration
        config = MatrixConfig(
            width=min(1200, screen_width),
            height=min(800, screen_height),
            fullscreen=False,
        )

        # Initialize the screen
        screen = _initialize_screen(config)

        # Create the matrix renderer and UI controls
        renderer = MatrixRenderer(config)
        ui_controls = UIControls(config, screen.get_width(), screen.get_height())

        # Main game loop
        clock = pygame.time.Clock()
        running = True

        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_f:
                        # Toggle fullscreen
                        config.fullscreen = not config.fullscreen
                        screen = _initialize_screen(config)
                        ui_controls.resize(screen.get_width(), screen.get_height())
                        renderer.resize(config)

                # Handle UI events
                ui_result = ui_controls.handle_event(event)
                if ui_result:
                    renderer.reset_matrix()

            # Update and render the matrix
            renderer.update()
            renderer.render(screen)

            # Draw UI controls
            ui_controls.draw(screen)

            # Update the display
            pygame.display.flip()

            # Control the frame rate
            clock.tick(60)

        # Clean up and exit
        pygame.quit()
        return 0

    except Exception as e:
        handle_error(e)
        return 1
    finally:
        pygame.quit()


def _initialize_screen(config: MatrixConfig) -> pygame.Surface:
    """
    Initialize or reinitialize the Pygame display.

    Args:
        config (MatrixConfig): The matrix configuration

    Returns:
        pygame.Surface: The initialized screen surface
    """
    flags = pygame.FULLSCREEN if config.fullscreen else 0
    screen = pygame.display.set_mode((config.width, config.height), flags)
    pygame.display.set_caption("Matrix Rain Animation")

    # Set up the icon
    try:
        icon = pygame.Surface((32, 32))
        icon.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 32)
        text = font.render("M", True, (0, 255, 0))
        icon.blit(text, (12, 8))
        pygame.display.set_icon(icon)

    except Exception as e:
        # Not critical, just log and continue
        print(f"Warning: Could not set icon: {e}")

    return screen


if __name__ == "__main__":
    sys.exit(main())
