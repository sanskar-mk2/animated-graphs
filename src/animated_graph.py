from typing import Iterator, Tuple
import pygame
import numpy as np
import pandas as pd
import time
from .color import Color
from .pg_app import PgApp
from .super_rect import SuperRect
from .graph import GraphConfig


class PygameExtended(PgApp):
    """Extended Pygame application with enhanced drawing capabilities."""

    def __init__(self, window_dimensions: tuple[int, int]) -> None:
        super().__init__(window_dimensions)

    def render_bar_labels(
        self, visualization_data: pd.DataFrame, visibility_flags: list[bool]
    ) -> None:
        """Draw text labels for bars.

        Args:
            visualization_data: DataFrame containing text renders and positions
            visibility_flags: List of booleans controlling label visibility
        """
        for text_surface, text_position, is_visible in zip(
            visualization_data["text_render"],
            visualization_data["text_rect"],
            visibility_flags,
        ):
            if is_visible:
                self.screen.blit(text_surface, text_position)

    def render_timestamp(
        self, timestamp_data: tuple[pygame.surface.Surface, pygame.rect.Rect]
    ) -> None:
        """Draw timestamp text.

        Args:
            timestamp_data: Tuple of timestamp surface and position
        """
        self.screen.blit(timestamp_data[0], timestamp_data[1])


class AnimatedBar(SuperRect):
    """Bar with animation properties."""

    def __init__(
        self,
        x_position: float,
        y_position: float,
        bar_width: float,
        bar_height: float,
        target_width: float,
        label: str,
        bar_color: Color,
        initial_width: int,
        final_width: int,
        initial_y: int,
        final_y: int,
    ) -> None:
        """Initialize animated bar.

        Args:
            x_position: X coordinate
            y_position: Y coordinate
            bar_width: Width of bar
            bar_height: Height of bar
            target_width: Target width for animation
            label: Bar label
            bar_color: Bar color
            initial_width: Starting width
            final_width: Ending width
            initial_y: Starting Y position
            final_y: Ending Y position
        """
        super().__init__(
            x_position,
            y_position,
            bar_width,
            bar_height,
            target_width,
            label,
            bar_color,
        )
        self.initial_width = initial_width
        self.final_width = final_width
        self.initial_y = initial_y
        self.final_y = final_y


class BarChartAnimation:
    """Animated bar chart visualization."""

    def __init__(
        self,
        pygame_app: PgApp,
        chart_data: pd.DataFrame,
        header_height: int,
        chart_config: GraphConfig,
    ) -> None:
        """Initialize animated bar chart.

        Args:
            pygame_app: Pygame application instance
            chart_data: DataFrame containing visualization data
            header_height: Height of header section
            chart_config: Chart configuration settings
        """
        self.pygame_app = pygame_app
        self.chart_data = chart_data
        self.chart_data[f"{list(self.chart_data.columns)[-1]}—"] = self.chart_data.iloc[
            :, -1
        ]
        self.time_points = chart_data.shape[1]
        self.num_bars = len(self.chart_data)

        # Header configuration
        self.header_rect = pygame.Rect(0, 0, pygame_app.width, header_height)

        # Bar configuration
        self.bar_height = chart_config.bar_height
        self.visible_bars = chart_config.to_show

        # Layout calculations
        self.vertical_gap = self._calculate_vertical_gap(header_height, chart_config)

        # Calculate max text width to adjust left gap
        temp_font = pygame.font.Font(
            chart_config.header_font, chart_config.small_text_size
        )
        max_text_width = max(
            temp_font.render(label, True, (0, 0, 0)).get_width()
            for label in chart_data.index
        )
        self.margin_left = max(
            chart_config.left_gap, max_text_width + chart_config.text_bar_distance + 20
        )

        # Calculate width multiplier based on available space
        max_value = chart_data.max().max()
        available_width = pygame_app.width - self.margin_left - 100  # Leave margin
        self.scale_factor = min(
            chart_config.width_multiplier, available_width / max_value
        )

        # Text configuration
        self.value_format = chart_config.value_prepost
        self.config = chart_config

        # Initialize components
        self.bars = []
        self._initialize_header(
            chart_config.header_font,
            chart_config.header_font_size,
            chart_config.header_text,
        )
        self._initialize_bars()
        self._initialize_labels(
            chart_config.small_text_size,
            chart_config.header_font,
            chart_config.text_bar_distance,
        )

        # Animation state
        self.current_frame = 0
        self.debug_mode = False
        self.animation_complete = False
        self.completion_timestamp = None

    def _calculate_vertical_gap(self, header_height: int, config: GraphConfig) -> float:
        """Calculate vertical spacing between bars."""
        available_height = (
            self.pygame_app.height
            - header_height
            - (config.to_show * config.bar_height)
        )
        return available_height / (1 + config.to_show)

    def _initialize_header(
        self, font_path: str, font_size: int, header_text: str
    ) -> None:
        """Initialize header text components."""
        self.header_font = pygame.font.Font(font_path, font_size)
        self.header_surface = self.header_font.render(
            header_text, True, Color.rgb_white()
        )
        self.header_position = self.header_surface.get_rect()
        self.header_position.center = (
            self.header_rect.width // 2,
            self.header_rect.height // 2,
        )

    def _initialize_bars(self) -> None:
        """Initialize bar objects and their positions."""
        self.chart_data = self.chart_data.sort_values(
            self.chart_data.columns[0], ascending=False
        )

        for idx, (key, value) in enumerate(
            zip(
                self.chart_data.index.to_series().to_list(),
                self.chart_data.iloc[:, 0].to_list(),
            )
        ):
            y_pos = self._calculate_bar_position(idx)
            color_idx = idx % len(self.config.colors)  # Wrap around colors if needed
            self.bars.append(
                AnimatedBar(
                    self.margin_left,
                    y_pos,
                    0,
                    self.bar_height,
                    value,
                    key,
                    self.config.colors[color_idx],
                    0,
                    value,
                    y_pos,
                    y_pos,
                )
            )

        self.chart_data["bars"] = self.bars

    def _calculate_bar_position(self, index: int) -> float:
        """Calculate vertical position for a bar."""
        return (
            self.header_rect.height
            + self.vertical_gap * (index + 1)
            + self.bar_height * index
        )

    def _initialize_labels(
        self, font_size: int, font_path: str, label_gap: int
    ) -> None:
        """Initialize static bar labels."""
        self.label_font = pygame.font.Font(font_path, font_size)
        text_surfaces = []
        text_positions = []

        for bar in self.chart_data["bars"]:
            surface = self.label_font.render(bar.title, True, Color.rgb_white())
            position = surface.get_rect()
            position.center = (position.center[0], bar.centery)
            position.right = self.margin_left - label_gap
            text_surfaces.append(surface)
            text_positions.append(position)

        self.chart_data["text_render"] = text_surfaces
        self.chart_data["text_rect"] = text_positions

    def animate(self, frame_duration: float) -> None:
        """Update animation state for current frame.

        Args:
            frame_duration: Duration of each animation frame
        """
        if self._should_advance_frame(frame_duration):
            self._update_frame()

        self._update_bar_animations(frame_duration)

    def _should_advance_frame(self, frame_duration: float) -> bool:
        """Determine if animation should advance to next frame."""
        return (
            frame_duration * (self.current_frame + 1) < self.pygame_app.time_elapsed
            and self.current_frame < self.time_points - 1
        )

    def _update_frame(self) -> None:
        """Update animation state for next frame."""
        self.current_frame += 1
        self.chart_data = self.chart_data.sort_values(
            self.chart_data.columns[self.current_frame], ascending=False
        )

        for idx, bar in enumerate(self.chart_data["bars"]):
            current_value = self.chart_data.iloc[
                self.chart_data.index.get_loc(bar.title), self.current_frame
            ]
            bar.initial_width = bar.final_width
            bar.final_width = current_value
            bar.initial_y = bar.final_y
            bar.final_y = self._calculate_bar_position(idx)

    def _update_bar_animations(self, frame_duration: float) -> None:
        """Update all bar positions and sizes."""
        elapsed = self.pygame_app.time_elapsed - self.current_frame * frame_duration
        for bar in self.chart_data["bars"]:
            self._animate_bar_width(bar, elapsed, frame_duration)
            self._animate_bar_position(bar, elapsed, frame_duration)

    def _animate_bar_width(
        self, bar: AnimatedBar, elapsed: float, duration: float
    ) -> None:
        """Animate bar width transition."""
        width_delta = (bar.final_width - bar.initial_width) / duration
        bar.width = (bar.initial_width + width_delta * elapsed) * self.scale_factor

    def _animate_bar_position(
        self, bar: AnimatedBar, elapsed: float, duration: float
    ) -> None:
        """Animate bar position transition."""
        position_delta = (bar.final_y - bar.initial_y) / duration
        bar.top = int(bar.initial_y + position_delta * elapsed)

    def update_label_positions(self) -> None:
        """Update vertical positions of bar labels."""
        for row in self.chart_data.itertuples():
            row.text_rect.centery = row.bars.centery

    def create_value_labels(
        self, right_margin: int, text_color: Color
    ) -> Iterator[Tuple[pygame.surface.Surface, pygame.rect.Rect, bool]]:
        """Create dynamic value labels for bars.

        Args:
            right_margin: Margin from right edge
            text_color: Label text color

        Yields:
            Tuple of (text surface, position rect, visibility flag)
        """
        for bar in self.bars:
            value_text = f"{self.value_format[0]}{int(bar.width // self.scale_factor)}{self.value_format[1]}"
            surface = self.label_font.render(value_text, True, text_color.rgb())
            position = surface.get_rect()
            position.right = bar.right - right_margin
            position.centery = bar.centery
            is_visible = bar.width > right_margin + position.width
            yield surface, position, is_visible

    def create_timestamp(
        self, position_type: str, text_color: Color, margin: int = 50
    ) -> tuple[pygame.surface.Surface, pygame.rect.Rect]:
        """Create timestamp display.

        Args:
            position_type: Position indicator ("BR" for bottom right)
            text_color: Timestamp color
            margin: Edge margin

        Returns:
            Tuple of timestamp surface and position
        """
        surface = self.header_font.render(
            str(self.chart_data.columns[self.current_frame]), True, text_color.rgb()
        )
        rect_position = surface.get_rect()

        if position_type == "BR":
            rect_position.right = self.pygame_app.width - margin
            rect_position.bottom = self.pygame_app.height - margin

        return surface, rect_position

    def check_animation_complete(self) -> bool:
        """Check if animation has finished.

        Returns:
            bool: True if animation is complete
        """
        self.animation_complete = self.current_frame >= self.time_points - 1
        if self.animation_complete and not self.completion_timestamp:
            self.completion_timestamp = time.time()
        return self.animation_complete

    def run(self) -> None:
        """Run the animation loop."""
        if self.config.record_path:
            self.pygame_app.recorder.start_rec(self.config.fps)

        while self.pygame_app.running:
            self.pygame_app.t0 = time.time()

            # Handle events
            for event in pygame.event.get():
                self.pygame_app.kill_switch(event)

            # Update animation state
            self.pygame_app.screen.fill(self.config.bg_color.rgb())
            self.animate(self.config.animation_speed)

            # Render frame
            self.pygame_app.draw_data_rects(
                self.bars,
                self.header_rect,
                self.config.header_bg_color,
                self.header_surface,
                self.header_position,
            )

            self.update_label_positions()
            self.pygame_app.render_bar_labels(
                self.chart_data, [bar.width > 0 for bar in self.bars]
            )

            value_labels = self.create_value_labels(
                self.config.value_gap, self.config.bg_color
            )
            timestamp = self.create_timestamp("BR", Color("#ffffff"), 200)

            self.pygame_app.render_timestamp(timestamp)
            self.pygame_app.draw_continuous_numbers(value_labels)

            # Update display
            self.pygame_app.update_display()
            self.pygame_app.fpsClock.tick(self.config.fps)
            self.pygame_app.time_elapsed += time.time() - self.pygame_app.t0

            # Check completion
            if self.check_animation_complete():
                if (
                    self.completion_timestamp
                    and time.time() - self.completion_timestamp
                    > self.config.wait_time_after_completion
                ):
                    if self.config.record_path:
                        self.pygame_app.recorder.stop_rec().save_recording(
                            self.config.record_path
                        )
                    self.pygame_app.running = False


if __name__ == "__main__":
    # Generate sample data
    num_items = 10
    num_frames = 20

    # Create random labels and initial values
    labels = [
        chr(int(x * 26) + 97) * np.random.randint(3, 10)
        for x in np.random.rand(num_items)
    ]
    initial_values = [int(x * 10) + 1 for x in np.random.rand(num_items)]

    # Generate time series data
    time_series = {}
    current_values = initial_values.copy()

    for frame in range(num_frames):
        time_series[frame] = dict(zip(labels, current_values))
        current_values = [v + np.random.randint(0, 10) for v in current_values]

    visualization_data = pd.DataFrame(time_series)

    # Initialize application
    WINDOW_SIZE = (1920, 1080)
    app = PygameExtended(WINDOW_SIZE)

    # Configure visualization
    chart_config = GraphConfig(
        header_font="./assets/Arial.ttf",
        header_font_size=69,
        header_text="Chart Visualization",
        bar_height=40,
        width_multiplier=10,
        colors=[
            Color("#f98284"),  # Red
            Color("#ffc384"),  # Orange
            Color("#dea38b"),  # Coral
            Color("#e9f59d"),  # Light Green
            Color("#fff7a0"),  # Yellow
            Color("#b0eb93"),  # Green
            Color("#b3e3da"),  # Teal
            Color("#accce4"),  # Light Blue
            Color("#b0a9e4"),  # Purple
            Color("#feaae4"),  # Pink
        ],
        left_gap=250,
        text_bar_distance=30,
        small_text_size=30,
        to_show=10,
        fps=60,
        animation_speed=0.5,
        bg_color=Color("#28282e"),
        header_bg_color=Color("#6c5671"),
        header_text_color=Color("#ffffff"),
        value_gap=10,
        record_path="animated_graph.mp4",
        wait_time_after_completion=3,
    )

    # Create and run visualization
    chart = BarChartAnimation(
        pygame_app=app,
        chart_data=visualization_data,
        header_height=100,
        chart_config=chart_config,
    )
    chart.run()
