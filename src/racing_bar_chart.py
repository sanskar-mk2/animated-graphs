from typing import Iterator
import pygame
import numpy as np
from color import Color
import time
import pandas as pd
from src.bar_chart_base import Graph, UberRect, PyGamer
from dataclasses import dataclass


@dataclass
class GraphTheme:
    """Defines the visual theme for the graph."""

    background_color: tuple[int, int, int] = Color("#28282e")
    header_color: tuple[int, int, int] = Color("#6c5671")
    text_color: tuple[int, int, int] = Color("#ffffff")
    bar_colors: list[tuple[int, int, int]] = None

    def __post_init__(self):
        if self.bar_colors is None:
            # Default color palette
            self.bar_colors = [
                Color("#f98284"),
                Color("#ffc384"),
                Color("#dea38b"),
                Color("#e9f59d"),
                Color("#fff7a0"),
                Color("#b0eb93"),
                Color("#b3e3da"),
                Color("#accce4"),
                Color("#b0a9e4"),
                Color("#feaae4"),
            ]


@dataclass
class LayoutConfig:
    """Defines the layout configuration for the graph."""

    width: int = 1280
    height: int = 720
    header_height: int = 80
    bar_height: int = 40
    bar_gap: int = 20
    left_margin: int = 200
    right_margin: int = 50
    text_bar_gap: int = 20
    value_prefix: str = ""
    value_suffix: str = ""


class PyGamerExt(PyGamer):
    def __init__(self, dimensions: tuple[int, int]) -> None:
        super().__init__(dimensions)

    def draw_rect_text(
        self,
        data: pd.DataFrame,  # list[tuple[pygame.surface.Surface, pygame.rect.Rect]],
        to_draw: list[bool],
    ):
        for rend, rect, draw in zip(data["text_render"], data["text_rect"], to_draw):
            if draw:
                self.screen.blit(rend, rect)

    def draw_dt(self, data):
        self.screen.blit(data[0], data[1])


class UberRectAnim(UberRect):
    def __init__(
        self,
        left: float,
        top: float,
        width: float,
        height: float,
        target: float,
        title: str,
        color: Color,
        start: int,
        finish: int,
        vstart: int,
        vfinish: int,
    ) -> None:
        super().__init__(left, top, width, height, target, title, color)
        self.start: int = start
        self.finish: int = finish
        self.vstart: int = vstart
        self.vfinish: int = vfinish


class BarManager:
    """Manages the bar-related logic and animations."""

    def __init__(
        self,
        data: pd.DataFrame,
        theme: GraphTheme,
        layout: LayoutConfig,
        left_gap: int,
        header_height: int,
        to_show: int,
    ):
        self.data = data
        self.theme = theme
        self.layout = layout
        self.bars = []
        self.left_gap = left_gap
        self.header_height = header_height
        self.to_show = to_show
        self.gap = self._calculate_gap(header_height)

    def _calculate_gap(self, header_height: int) -> float:
        return (
            self.layout.height - header_height - (self.to_show * self.layout.bar_height)
        ) / (1 + self.to_show)

    def initialize_bars(self):
        """Initialize the bars with their initial positions and properties."""
        self.data = self.data.sort_values(self.data.columns[0], ascending=False)
        k_v_pair = zip(
            self.data.index.to_series().to_list(), self.data.iloc[:, 0].to_list()
        )

        for idx, (k, v) in enumerate([i for i in k_v_pair]):
            bar = UberRectAnim(
                left=self.left_gap,
                top=self.header_height
                + self.gap * (idx + 1)
                + self.layout.bar_height * idx,
                width=0,
                height=self.layout.bar_height,
                target=v,
                title=k,
                color=self.theme.bar_colors[idx % len(self.theme.bar_colors)],
                start=0,
                finish=v,
                vstart=self.header_height
                + self.gap * (idx + 1)
                + self.layout.bar_height * idx,
                vfinish=self.header_height
                + self.gap * (idx + 1)
                + self.layout.bar_height * idx,
            )
            self.bars.append(bar)

        self.data["bars"] = self.bars
        return self.bars

    @staticmethod
    def animate_bar_width(
        bar: "UberRectAnim", delta_time: float, time_each: float, width_mult: float
    ):
        """Animate the width of a bar."""
        change_per_ms = (bar.finish - bar.start) / time_each
        bar.width = (bar.start + change_per_ms * delta_time) * width_mult

    @staticmethod
    def animate_bar_position(bar: "UberRectAnim", delta_time: float, time_each: float):
        """Animate the vertical position of a bar."""
        change_per_ms = (bar.vfinish - bar.vstart) / time_each
        bar.top = int(bar.vstart + change_per_ms * delta_time)

    def update_bar_positions(self, current_time: int, time_each: float):
        """Update all bar positions for the current frame."""
        self.data = self.data.sort_values(
            self.data.columns[current_time], ascending=False
        )

        for idx, bar in enumerate(self.data["bars"]):
            bar.start = bar.finish
            bar.finish = self.data.iloc[
                self.data.index.get_loc(bar.title), current_time
            ]
            bar.vstart = bar.vfinish
            bar.vfinish = (
                self.header_height + self.gap * (idx + 1) + self.layout.bar_height * idx
            )


class AnimatedGraph(Graph):
    def __init__(
        self,
        pgapp: PyGamer,
        data: pd.DataFrame,
        header_text: str,
        header_font_size: int,
        header_font: str,
        width_multiplier: float,
        left_gap: int,
        text_bar_distance: int = 20,
        small_text_size=40,
        to_show: int = 10,
        debug: bool = False,
        theme: GraphTheme = GraphTheme(),
        layout: LayoutConfig = LayoutConfig(),
    ) -> None:
        self.pgapp: PyGamer = pgapp
        self.data: pd.DataFrame = data
        self.theme: GraphTheme = theme
        self.layout: LayoutConfig = layout
        self.data[f"{list(self.data.columns)[-1]}—"] = self.data.iloc[:, -1]
        self.dt_len = data.shape[1]
        self.bars_count: int = len(self.data)
        self.header: pygame.Rect = pygame.Rect(
            0, 0, pgapp.aw, self.layout.header_height
        )
        self.width_multiplier: float = width_multiplier
        self.bars: list[UberRectAnim] = list()
        self.to_show = to_show
        self.gap: float = (
            self.pgapp.ah - self.header.height - (self.to_show * self.layout.bar_height)
        ) / (1 + self.to_show)
        self.left_gap = left_gap
        self.create_header(header_font, header_font_size, header_text)

        self.seed_rectangles()
        self.create_text_render(small_text_size, header_font, text_bar_distance)
        self.at: int = 0
        self.debug: bool = debug

    def seed_rectangles(self):
        self.data = self.data.sort_values(self.data.columns[0], ascending=False)
        k_v_pair = zip(
            self.data.index.to_series().to_list(), self.data.iloc[:, 0].to_list()
        )
        for idx, (k, v) in enumerate([i for i in k_v_pair]):
            self.bars.append(
                UberRectAnim(
                    self.left_gap,
                    self.header.height
                    + self.gap * (idx + 1)
                    + self.layout.bar_height * idx,
                    0,
                    self.layout.bar_height,
                    v,
                    k,
                    self.theme.bar_colors[idx % len(self.theme.bar_colors)],
                    0,
                    v,
                    self.header.height
                    + self.gap * (idx + 1)
                    + self.layout.bar_height * idx,
                    self.header.height
                    + self.gap * (idx + 1)
                    + self.layout.bar_height * idx,
                )
            )

        self.data["bars"] = self.bars

    def simultaneous_grow(self, time_each):
        for item in self.bars:
            if item.width < item.target:
                item.width = self.increment_rect(
                    item.target, self.pgapp.time_elapsed, time_each
                )

    def animated_grow(self, time_each):
        if time_each * (self.at + 1) < self.pgapp.time_elapsed:
            if self.at < self.dt_len - 1:
                self.at += 1
            else:
                return
            self.data = self.data.sort_values(
                self.data.columns[self.at], ascending=False
            )
            if self.debug:
                print(self.data)
            for idx, item in enumerate(self.data["bars"]):
                item.start = item.finish
                item.finish = self.data.iloc[
                    self.data.index.get_loc(item.title), self.at
                ]
                # vertical
                item.vstart = item.vfinish
                item.vfinish = (
                    self.header.height
                    + self.gap * (idx + 1)
                    + self.layout.bar_height * idx
                )
        for item in self.data["bars"]:
            # if item.width < item.finish:
            AnimatedGraph.change_rect_w(
                item,
                self.pgapp.time_elapsed - self.at * time_each,
                time_each,
                self.width_multiplier,
            )
            AnimatedGraph.change_rect_v(
                item, self.pgapp.time_elapsed - self.at * time_each, time_each
            )

    @staticmethod
    def change_rect_w(r: UberRectAnim, deltat: float, time_each: float, width_mult):
        change_per_ms = (r.finish - r.start) / time_each
        r.width = (r.start + change_per_ms * deltat) * width_mult

    @staticmethod
    def change_rect_v(r: UberRectAnim, deltat: float, time_each: float):
        change_per_ms = (r.vfinish - r.vstart) / time_each
        r.top = int(r.vstart + change_per_ms * deltat)

    def create_continuous_renders(
        self, gap_from_right, color: Color
    ) -> Iterator[tuple[pygame.surface.Surface, pygame.rect.Rect, bool]]:
        for obj in self.bars:
            render = self.text_font_obj.render(
                # check whats writen in base class if needed
                f"{self.layout.value_prefix}{obj.width // self.width_multiplier}{self.layout.value_suffix}",
                True,
                color.rgb(),
            )
            render_rect: pygame.rect.Rect = render.get_rect()
            render_rect.right = obj.right - gap_from_right
            render_rect.centery = obj.centery
            yield render, render_rect, obj.width > gap_from_right + render_rect.width

    def create_text_render(self, font_size, header_font, extra_gap):
        self.renderls: list[pygame.surface.Surface] = list()
        self.render_rectls: list[pygame.rect.Rect] = list()
        # this needs to run before create_continuous_render since it creates the
        self.text_font_obj = pygame.font.Font(header_font, font_size)
        for obj in self.data["bars"]:
            render = self.text_font_obj.render(
                obj.title, True, self.theme.text_color.rgb()
            )
            render_rect = render.get_rect()
            render_rect.center = (render_rect.center[0], obj.centery)
            render_rect.right = self.left_gap - extra_gap
            self.renderls.append(render)
            self.render_rectls.append(render_rect)

        self.data["text_render"] = self.renderls
        self.data["text_rect"] = self.render_rectls

    def move_text_renders(self):
        for item in self.data.itertuples():
            item.text_rect.centery = item.bars.centery

    def dt_renders(self, where: str, color, distance=50):
        render = self.header_font.render(
            str(self.data.columns[self.at]),
            True,
            color.rgb(),
        )
        render_rect: pygame.rect.Rect = render.get_rect()
        if where == "BR":
            render_rect.right = self.pgapp.aw - distance
            render_rect.bottom = self.pgapp.ah - distance

        return render, render_rect

    def run(self):
        while self.pgapp.running:
            self.pgapp.t0 = time.time()
            for event in pygame.event.get():
                self.pgapp.kill_switch(event)

            self.pgapp.screen.fill(self.theme.background_color.rgb())
            self.animated_grow(0.1)
            self.pgapp.draw_data_rects(
                self.bars,
                self.header,
                self.theme.header_color,
                self.header_text_render,
                self.header_text_rect,
            )

            self.move_text_renders()
            self.pgapp.draw_rect_text(self.data, [bar.width > 0 for bar in self.bars])
            renders = self.create_continuous_renders(10, self.theme.text_color)
            dt_renders = self.dt_renders("BR", self.theme.text_color, 200)
            self.pgapp.draw_dt(dt_renders)
            self.pgapp.draw_continuous_numbers(renders)
            self.pgapp.update_display()
            self.pgapp.fpsClock.tick(60)
            self.pgapp.time_elapsed += time.time() - self.pgapp.t0


if __name__ == "__main__":
    FONT: str = (
        "./assets/fonts/Kelvinch-Bold.otf"  # "./res/Shaky Hand Some Comic_bold.otf"
    )
    TIME_EACH: float = 0.5
    FPS: int = 60
    TITLE: str = "Test Title"

    # the k_v_pair will contain the title of the bar and the total value of the bar in a k, v pair tuple
    # k_v_pair: list[tuple[str, int]] = []

    # to display the image on the right side, make a column of images of same length as k_v_pair,
    # the PIL.Image should have ImageUtil.get_images_ready to run on them to crop them and convert to pygame.Surface
    # a: list[pygame.Surface] = []

    # start doing data farm here
    """
    df = pd.read_csv("./Datadone.csv")

    df = df.head(20)
    df.at[6, "name"] = "Kochikame"
    k = df.loc[:, "name"]
    v = df.loc[:, "numeps"]
    k_v_pair = [(k, v) for k, v in zip(k, v)]


    ims: list[pygame.surface.Surface] = []
    for i in range(1, 81):
        im = Image.open(f"./LAS/{i}.jpg")
        im = ImageUtil.get_images_ready(im, 50, True, True, 0)
        ims.append(im)

    a, b, c, d = np.array(ims).reshape(20, 4).transpose()
    """
    # end doing data farm here

    # Create Dummy Data
    keys = map(
        lambda x: chr(int(x * 26) + 97) * np.random.randint(3, 10), np.random.rand(10)
    )
    v0 = map(lambda x: int(x * 10) + 1, np.random.rand(10))

    """
    having it in list is not best, cause timestamps will be used as keys
    

    for i in range(1, 10):
        v = map(lambda x: int(x * 5) + 1, np.random.rand(10))
        values.append([j for j in map(lambda x: x + next(v), values[i - 1])])

    k_vs_pair = zip(keys, *values)
    for k, *vs in k_vs_pair:
        print(f"{k} = {vs[0]}")
    exit()
    """

    # key-time-value format

    # time-key-value format\
    kv_dict: dict = dict()
    keys_lst = [i for i in keys]
    v0_lst = [i for i in v0]
    for i in range(20):
        kv_dict.update({i: {}})
        for idx, k in enumerate(keys_lst):
            kv_dict[i].update({k: v0_lst[idx]})
        v0_lst = [a + np.random.randint(0, 10) for a in v0_lst]

    df = pd.DataFrame(kv_dict)
    print(df)

    # assert len(a) == len(k_v_pair)
    pastels = [
        Color("#f98284"),
        Color("#ffc384"),
        Color("#dea38b"),
        Color("#e9f59d"),
        Color("#fff7a0"),
        Color("#b0eb93"),
        Color("#b3e3da"),
        Color("#accce4"),
        Color("#b0a9e4"),
        Color("#feaae4"),
        Color("#f98284"),
        Color("#ffc384"),
        Color("#dea38b"),
        Color("#e9f59d"),
        Color("#fff7a0"),
        Color("#b0eb93"),
        Color("#b3e3da"),
        Color("#accce4"),
        Color("#b0a9e4"),
        Color("#feaae4"),
    ]
    bg_color = Color("#28282e")
    header_color = Color("#6c5671")

    SIZE = 1920, 1080
    app = PyGamerExt(SIZE)
    graph = AnimatedGraph(
        pgapp=app,
        data=df,
        header=100,
        header_text=TITLE,
        header_font_size=69,
        header_font=FONT,
        bar_height=40,
        width_multiplier=10,
        colors=pastels,
        left_gap=250,
        text_bar_distance=30,
        small_text_size=30,
    )
    while app.running:
        app.t0 = time.time()
        for event in pygame.event.get():
            app.kill_switch(event)

        app.screen.fill(bg_color.rgb())
        graph.animated_grow(TIME_EACH)
        app.draw_data_rects(
            graph.bars,
            graph.header,
            header_color,
            graph.header_text_render,
            graph.header_text_rect,
        )
        graph.move_text_renders()
        app.draw_rect_text(graph.data, [bar.width > 0 for bar in graph.bars])
        renders = graph.create_continuous_renders(10, bg_color)
        dt_renders = graph.dt_renders("BR", Color("#ffffff"), 200)
        app.draw_dt(dt_renders)
        app.draw_continuous_numbers(renders)
        # app.draw_image_on_right(0, a, graph.bars)
        # app.draw_image_on_right(1, b, graph.bars)
        # app.draw_image_on_right(2, c, graph.bars)
        # app.draw_image_on_right(3, d, graph.bars)
        app.update_display()
        app.fpsClock.tick(FPS)
        app.time_elapsed += time.time() - app.t0
