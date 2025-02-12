import pygame
from color import Color
from super_rect import SuperRect
from pygame_screen_record import ScreenRecorder, add_codec


class Display:
    """Handles display-related operations and drawing."""

    def __init__(self, screen: pygame.surface.Surface):
        self.screen = screen

    def update(self):
        pygame.display.update()

    def draw_rect_with_header(
        self,
        rect: pygame.Rect,
        color: Color,
        header_text: pygame.surface.Surface,
        header_rect: pygame.rect.Rect,
    ):
        pygame.draw.rect(self.screen, color.rgb(), rect)
        self.screen.blit(header_text, header_rect)

    def draw_data_rects(
        self,
        data: list[SuperRect],
        header: pygame.Rect,
        header_color: Color,
        header_render: pygame.surface.Surface,
        header_rend_rect: pygame.rect.Rect,
    ):
        self.draw_rect_with_header(
            header, header_color, header_render, header_rend_rect
        )
        for item in data:
            pygame.draw.rect(self.screen, item.color.rgb(), item.as_rect())

    def draw_rect_text(
        self,
        data: list[tuple[pygame.surface.Surface, pygame.rect.Rect]],
        to_draw: list[bool],
    ):
        for item, draw in zip(data, to_draw):
            if draw:
                self.screen.blit(item[0], item[1])

    def draw_continuous_numbers(
        self, data: list[tuple[pygame.surface.Surface, pygame.rect.Rect, bool]]
    ):
        for render, rect, to_draw in data:
            if to_draw:
                self.screen.blit(render, rect)

    def draw_image_on_right(
        self, column: int, images: list[pygame.surface.Surface], position_data: list
    ):
        for img, obj in zip(images, position_data):
            if obj.width > 0:
                self.screen.blit(img, (obj.right - 5 + column * 40, obj.centery - 25))


class EventHandler:
    """Handles pygame events and game state."""

    def __init__(self):
        self.running = True

    def handle_event(self, event: pygame.event.EventType) -> None:  # type: ignore
        """Handle quit and escape key events.

        Args:
            event: Pygame event to process
        """
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False


class PgApp:
    """Main game application class."""

    def __init__(
        self, dimensions: tuple[int, int],
    ) -> None:
        """Initialize the game window and components.

        Args:
            dimensions: Tuple of (width, height) for window size
        """
        pygame.init()
        self.width, self.height = dimensions
        self.screen = pygame.display.set_mode(dimensions, pygame.NOFRAME)
        self.display = Display(self.screen)
        self.event_handler = EventHandler()
        self.running = True
        self.t0: float = 0.0
        self.time_elapsed: float = 0.0
        self.fpsClock = pygame.time.Clock()
        self.recorder = ScreenRecorder()
        add_codec("mp4", "mp4v")

    def update_display(self):
        self.display.update()

    def draw_data_rects(self, *args, **kwargs):
        self.display.draw_data_rects(*args, **kwargs)

    def draw_rect_text(self, *args, **kwargs):
        self.display.draw_rect_text(*args, **kwargs)

    def draw_continuous_numbers(self, *args, **kwargs):
        self.display.draw_continuous_numbers(*args, **kwargs)

    def draw_image_on_right(self, *args, **kwargs):
        self.display.draw_image_on_right(*args, **kwargs)

    def kill_switch(self, event: pygame.event.EventType) -> None:
        self.event_handler.handle_event(event)
        self.running = self.event_handler.running
