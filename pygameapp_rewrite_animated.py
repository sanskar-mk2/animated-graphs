from typing import Iterator, Sequence
import pygame
from color import Color
import time
from PIL import Image, ImageDraw  # type: ignore
import math
import pandas as pd  # type: ignore
import numpy as np
import pprint
from pygameapp_rewrite import Graph, UberRect, PyGamer


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


class AnimatedGraph(Graph):
    def __init__(
        self,
        pgapp: PyGamer,
        data: pd.DataFrame,
        header: int,
        header_text: str,
        header_font_size: int,
        header_font: str,
        bar_height: int,
        width_multiplier: float,
        colors: list[Color],
        left_gap: int,
        text_bar_distance: int = 20,
        small_text_size=40,
    ) -> None:
        self.pgapp: PyGamer = pgapp
        self.data: pd.DataFrame = data
        self.dt_len = data.shape[1]
        self.bars_count: int = len(data)
        self.header: pygame.Rect = pygame.Rect(0, 0, pgapp.aw, header)
        self.bar_height: int = bar_height
        self.width_multiplier: float = width_multiplier
        self.bars: list[UberRectAnim] = list()
        self.gap: float = (
            self.pgapp.ah - self.header.height - (self.bars_count * bar_height)
        ) / (1 + self.bars_count)
        self.colors: list[Color] = colors
        self.left_gap = left_gap

        self.create_header(header_font, header_font_size, header_text)

        self.seed_rectangles()
        self.create_text_render(small_text_size, header_font, text_bar_distance)
        self.at: int = 0

    def seed_rectangles(self):
        self.data = self.data.sort_values(0, ascending=False)
        k_v_pair = zip(
            self.data.index.to_series().to_list(), self.data.iloc[:, 0].to_list()
        )
        for idx, (k, v) in enumerate([i for i in k_v_pair]):
            self.bars.append(
                UberRectAnim(
                    self.left_gap,
                    self.header.height + self.gap * (idx + 1) + self.bar_height * idx,
                    0,
                    self.bar_height,
                    v,
                    k,
                    self.colors[idx],
                    0,
                    v,
                    self.header.height + self.gap * (idx + 1) + self.bar_height * idx,
                    self.header.height + self.gap * (idx + 1) + self.bar_height * idx,
                )
            )

        self.data["bars"] = self.bars
        print(self.data)

    def simultaneous_grow(self, time_each):
        for item in self.bars:
            if item.width < item.target:
                item.width = self.increment_rect(
                    item.target, self.pgapp.time_elapsed, time_each
                )

    def animated_grow(self, time_each):
        # for ts in range(len(self.data.columns)):
        # if self.pgapp.time_elapsed // time_each
        if time_each * (self.at + 1) < self.pgapp.time_elapsed:
            print("hit", self.pgapp.time_elapsed)
            if self.at < self.dt_len - 1:
                self.at += 1
            else:
                return
            self.data = self.data.sort_values(self.at, ascending=False)
            for idx, item in enumerate(self.data["bars"]):
                item.start = item.finish
                item.finish = self.data.loc[item.title][self.at]
                # vertical
                item.vstart = item.vfinish
                item.vfinish = (
                    self.header.height + self.gap * (idx + 1) + self.bar_height * idx
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
                str(obj.width // self.width_multiplier),
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
            render = self.text_font_obj.render(obj.title, True, Color.rgb_white())
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
            str(self.at),
            True,
            color.rgb(),
        )
        render_rect: pygame.rect.Rect = render.get_rect()
        if where == "BR":
            render_rect.right = self.pgapp.aw - distance
            render_rect.bottom = self.pgapp.ah - distance

        return render, render_rect


if __name__ == "__main__":
    FONT: str = "./assets/fonts/Kelvinch-Bold.otf"  # "./res/Shaky Hand Some Comic_bold.otf"
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
        pygame.display.update()
        app.fpsClock.tick(FPS)
        app.time_elapsed += time.time() - app.t0
