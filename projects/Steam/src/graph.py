from .color import Color
import math
from .super_rect import SuperRect
import pygame
import time
from typing import Iterator, Tuple
from .pg_app import PgApp


class GraphConfig:
    """Configuration settings for graph appearance and behavior."""

    def __init__(
        self,
        header_font: str,
        header_font_size: int,
        header_text: str,
        bar_height: int,
        width_multiplier: float,
        colors: list[Color],
        left_gap: int,
        text_bar_distance: int = 20,
        small_text_size: int = 40,
        to_show: int = 10,
        value_prepost: tuple[str, str] = (str(), str()),
        fps: int = 60,
        animation_speed: float = 0.05,
        bg_color: Color = Color("#000000"),
        header_bg_color: Color = Color("#FFFFFF"),
        header_text_color: Color = Color("#000000"),
        value_gap: int = 10,
        animation_type: str = "bottom_up",
        record_path: str = "",
        wait_time_after_completion: int = 3,
    ) -> None:
        """Initialize graph configuration.

        Args:
            header_font: Path to font file for header text
            header_font_size: Font size for header text
            header_text: Text to display in header
            bar_height: Height of each bar in pixels
            width_multiplier: Scale factor for bar widths
            colors: List of colors for bars
            left_gap: Space between left edge and bars
            text_bar_distance: Space between text and bars
            small_text_size: Font size for bar labels
            to_show: Number of bars to display
            value_prepost: Tuple of (prefix, suffix) for values
            fps: Frames per second for animation
            animation_speed: Time in seconds for each bar's growth
            bg_color: Background color
            header_bg_color: Header background color
            header_text_color: Header text color
            value_gap: Gap between value text and bar edge
            animation_type: Type of animation ("simultaneous", "top_down", "bottom_up")
            record_path: Path to save the recording
            wait_time_after_completion: Time to wait after completion before saving the recording
        """
        self.header_font = header_font
        self.header_font_size = header_font_size
        self.header_text = header_text
        self.bar_height = bar_height
        # Adjust width multiplier based on screen width
        screen_info = pygame.display.Info()
        max_width = screen_info.current_w - left_gap - 100  # Leave some margin
        self.width_multiplier = min(width_multiplier, max_width)
        self.colors = colors
        self.left_gap = left_gap
        self.text_bar_distance = text_bar_distance
        self.small_text_size = small_text_size
        self.to_show = to_show
        self.value_prepost = value_prepost
        self.fps = fps
        self.animation_speed = animation_speed
        self.bg_color = bg_color
        self.header_bg_color = header_bg_color
        self.header_text_color = header_text_color
        self.value_gap = value_gap
        self.animation_type = animation_type
        self.record_path = record_path
        self.wait_time_after_completion = wait_time_after_completion


class GraphHeader:
    """Handles the header section of the graph."""

    def __init__(self, config: GraphConfig, app_width: int, header_height: int) -> None:
        """Initialize header with text and positioning.

        Args:
            config: Graph configuration settings
            app_width: Width of application window
            header_height: Height of header section
        """
        self.rect = pygame.Rect(0, 0, app_width, header_height)
        self.font = pygame.font.Font(config.header_font, config.header_font_size)
        self.text_render = self.font.render(
            config.header_text, True, config.header_text_color.rgb()
        )
        self.text_rect = self.text_render.get_rect()
        self.text_rect.center = self.rect.width // 2, self.rect.height // 2


class BarManager:
    """Manages the collection of bars in the graph."""

    def __init__(
        self,
        config: GraphConfig,
        header_height: int,
        app_height: int,
        data: list[tuple[str, int]],
    ) -> None:
        """Initialize bars with proper spacing and dimensions.

        Args:
            config: Graph configuration settings
            header_height: Height of header section
            app_height: Total height of application window
            data: List of (label, value) tuples for bars
        """
        self.bars = []
        self.gap = (
            app_height - header_height - (config.to_show * config.bar_height)
        ) / (1 + config.to_show)

        # Calculate max text width to adjust left gap
        temp_font = pygame.font.Font(config.header_font, config.small_text_size)
        max_text_width = max(
            temp_font.render(label, True, (0, 0, 0)).get_width() for label, _ in data
        )
        adjusted_left_gap = max(
            config.left_gap, max_text_width + config.text_bar_distance + 20
        )

        # Adjust width multiplier based on available space
        max_value = max(value for _, value in data)
        available_width = pygame.display.Info().current_w - adjusted_left_gap - 100
        width_multiplier = min(config.width_multiplier, available_width / max_value)

        for idx, (label, value) in enumerate(data):
            self.bars.append(
                SuperRect(
                    adjusted_left_gap,
                    header_height + self.gap * (idx + 1) + config.bar_height * idx,
                    0,
                    config.bar_height,
                    value * width_multiplier,
                    label,
                    config.colors[idx % len(config.colors)],
                )
            )


class TextRenderer:
    """Handles text rendering for the graph."""

    def __init__(self, config: GraphConfig, bars: list[SuperRect]) -> None:
        """Initialize text renderer with font and label positions.

        Args:
            config: Graph configuration settings
            bars: List of bar rectangles to label
        """
        self.font = pygame.font.Font(config.header_font, config.small_text_size)
        self.renders = []

        for bar in bars:
            render = self.font.render(bar.title, True, config.header_bg_color.rgb())
            render_rect = render.get_rect()
            render_rect.center = (render_rect.center[0], bar.centery)
            render_rect.right = bar.x - config.text_bar_distance
            self.renders.append((render, render_rect))

    def create_continuous_renders(
        self,
        bars: list[SuperRect],
        gap_from_right: int,
        color: Color,
        width_multiplier: float,
        value_prepost: tuple[str, str],
    ) -> Iterator[Tuple[pygame.surface.Surface, pygame.rect.Rect, bool]]:
        """Create value labels that update as bars grow.

        Args:
            bars: List of bar rectangles
            gap_from_right: Space between value and right edge of bar
            color: Color for value text
            width_multiplier: Scale factor for values
            value_prepost: Tuple of (prefix, suffix) for values

        Yields:
            Tuple of (text surface, position rect, visibility flag)
        """
        for bar in bars:
            value = str(
                int(bar.width // width_multiplier)
                if bar.width < bar.target
                else int(bar.target // width_multiplier)
            )
            value = f"{value_prepost[0]}{value}{value_prepost[1]}"
            render = self.font.render(value, True, color.rgb())
            render_rect = render.get_rect()
            render_rect.right = bar.right - gap_from_right
            render_rect.centery = bar.centery
            yield render, render_rect, bar.width > gap_from_right + render_rect.width


class Graph:
    def __init__(
        self,
        pgapp: PgApp,
        data: list[tuple[str, int]],
        header_height: int,
        config: GraphConfig,
    ) -> None:
        """Initialize graph with data and configuration.

        Args:
            pgapp: Pygame application instance
            data: List of (label, value) tuples for bars
            header_height: Height of header section
            config: Graph configuration settings
        """
        self.pgapp = pgapp
        self.data = data
        self.bars_count = len(data)
        self.config = config

        self.header = GraphHeader(config, pgapp.width, header_height)
        self.bar_manager = BarManager(config, header_height, pgapp.height, data)
        self.text_renderer = TextRenderer(config, self.bar_manager.bars)
        self.bars = self.bar_manager.bars
        self.store_rect_render = self.text_renderer.renders
        self.is_complete = False
        self.completion_time = None

    def check_completion(self) -> bool:
        """Check if all bars have reached their target width.

        Returns:
            bool: True if all bars are complete, False otherwise
        """
        self.is_complete = all(bar.width >= bar.target for bar in self.bars)
        if self.is_complete and not self.completion_time:
            self.completion_time = time.time()
        return self.is_complete

    def simultaneous_grow(self, time_each: float) -> None:
        """Grow all bars simultaneously.

        Args:
            time_each: Time in seconds for full growth
        """
        for item in self.bars:
            if item.width < item.target:
                item.width = self._increment_rect(
                    item.target, self.pgapp.time_elapsed, time_each
                )

    def simultaneous_grow_flat(self, speed_multiplier: float) -> None:
        """Grow all bars simultaneously with flat animation speed.

        Args:
            speed_multiplier: Speed multiplier for flat animation
        """
        for item in self.bars:
            if item.width < item.target:
                item.width = self._increment_rect_flat(
                    item.target, self.pgapp.time_elapsed, speed_multiplier
                )

    def top_down_grow(self, time_each: float) -> None:
        """Grow bars sequentially from top to bottom.

        Args:
            time_each: Time in seconds for each bar's growth
        """
        for idx, item in enumerate(self.bars):
            if item.width < item.target:
                item.width = self._increment_rect(
                    item.target, self.pgapp.time_elapsed - idx * time_each, time_each
                )

    def top_down_grow_flat(self, speed_multiplier: float) -> None:
        """Grow bars sequentially from top to bottom with flat animation speed.

        Args:
            speed_multiplier: Speed multiplier for flat animation
        """
        for idx, item in enumerate(self.bars):
            if idx > 0 and self.bars[idx - 1].width < self.bars[idx - 1].target:
                continue
            if item.width < item.target:
                # Calculate total time taken by previous bars
                previous_time = (
                    sum(bar.target / speed_multiplier for bar in self.bars[:idx]) / 100
                )

                item.width = self._increment_rect_flat(
                    item.target,
                    self.pgapp.time_elapsed - previous_time,
                    speed_multiplier,
                )

    def bottom_up_grow(self, time_each: float) -> None:
        """Grow bars sequentially from bottom to top.

        Args:
            time_each: Time in seconds for each bar's growth
        """
        for idx, item in enumerate(self.bars[::-1]):
            if item.width < item.target:
                item.width = self._increment_rect(
                    item.target, self.pgapp.time_elapsed - idx * time_each, time_each
                )

    def bottom_up_grow_flat(self, speed_multiplier: float) -> None:
        """Grow bars sequentially from bottom to top with flat animation speed.

        Args:
            speed_multiplier: Speed multiplier for flat animation
        """
        for idx, item in enumerate(self.bars[::-1]):
            # Don't start growing current bar until previous bar (the one below) is done
            if (
                idx > 0
                and self.bars[::-1][idx - 1].width < self.bars[::-1][idx - 1].target
            ):
                continue
            if item.width < item.target:
                # Calculate total time taken by previous bars (the ones below)
                previous_time = (
                    sum(bar.target / speed_multiplier for bar in self.bars[::-1][:idx])
                    / 100
                )

                item.width = self._increment_rect_flat(
                    item.target,
                    self.pgapp.time_elapsed - previous_time,
                    speed_multiplier,
                )

    def create_continuous_renders(
        self, gap_from_right: int, color: Color
    ) -> Iterator[Tuple[pygame.surface.Surface, pygame.rect.Rect, bool]]:
        """Create value labels for current bar widths.

        Args:
            gap_from_right: Space between value and right edge of bar
            color: Color for value text

        Returns:
            Iterator of render tuples for value labels
        """
        return self.text_renderer.create_continuous_renders(
            self.bars,
            gap_from_right,
            color,
            self.config.width_multiplier,
            self.config.value_prepost,
        )

    @staticmethod
    def _increment_rect(target: float, deltat: float, time_each: float) -> int:
        """Calculate incremental width for smooth bar growth.

        Args:
            target: Target width for bar
            deltat: Time elapsed since start
            time_each: Total time for growth

        Returns:
            New width value for bar
        """
        increment_per_ms = target / (time_each * 100)
        return round(deltat * increment_per_ms * 100)

    @staticmethod
    def _increment_rect_flat(target: float, deltat: float, value: float) -> int:
        """Calculate incremental width for smooth bar growth with flat animation speed.

        Args:
            target: Target width for bar
            deltat: Time elapsed since start
            value: Value per second for flat animation

        Returns:
            New width value for bar
        """

        return round(deltat * value * 100)

    @staticmethod
    def roundup(x: float) -> int:
        """Round up to nearest hundred.


        Args:
            x: Value to round up

        Returns:
            Rounded value
        """
        return int(math.ceil(x / 100.0)) * 100

    def run(self) -> None:
        """Run the graph animation loop."""
        animation_methods = {
            "simultaneous": self.simultaneous_grow,
            "top_down": self.top_down_grow,
            "bottom_up": self.bottom_up_grow,
            "simultaneous_flat": self.simultaneous_grow_flat,
            "top_down_flat": self.top_down_grow_flat,
            "bottom_up_flat": self.bottom_up_grow_flat,
        }

        if self.config.record_path:
            self.pgapp.recorder.start_rec(self.config.fps)

        while self.pgapp.running:
            self.pgapp.t0 = time.time()
            for event in pygame.event.get():
                self.pgapp.kill_switch(event)

            # Draw frame
            self.pgapp.screen.fill(self.config.bg_color.rgb())
            animation_methods[self.config.animation_type](self.config.animation_speed)
            self.pgapp.draw_data_rects(
                self.bars,
                self.header,
                self.config.header_bg_color,
                self.header.text_render,
                self.header.text_rect,
            )
            self.pgapp.draw_rect_text(
                self.store_rect_render, [bar.width > 0 for bar in self.bars]
            )
            renders = self.create_continuous_renders(
                self.config.value_gap, self.config.bg_color
            )
            self.pgapp.draw_continuous_numbers(renders)

            # Update display
            self.pgapp.update_display()
            self.pgapp.fpsClock.tick(self.config.fps)
            self.pgapp.time_elapsed += time.time() - self.pgapp.t0

            if self.check_completion():
                if (
                    self.completion_time
                    and time.time() - self.completion_time
                    > self.config.wait_time_after_completion
                ):
                    if self.config.record_path:
                        self.pgapp.recorder.stop_rec().save_recording(
                            self.config.record_path
                        )
                    self.pgapp.running = False
