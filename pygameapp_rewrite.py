import abc
from typing import Iterator
import numpy
import pygame
from color import Color
import time
from PIL import Image, ImageDraw  # type: ignore
import math
import pandas as pd  # type: ignore
import numpy as np


class ImageUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def pilImageToSurface(pilImage) -> pygame.surface.Surface:
        return pygame.image.fromstring(pilImage.tobytes(), pilImage.size, pilImage.mode)

    @staticmethod
    def circumsize(im) -> Image:
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new("L", bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)
        return im

    @staticmethod
    def get_images_ready(
        im: Image, sz: int, should_circle: bool, to_crop: bool, crop_where: int
    ) -> pygame.surface.Surface:
        """
        About `crop_where`: takes 0, 1, 2 as argument, if image is vertical,
        makes a square crop at top, center, bottom for 0, 1, 2 respectively.
        And if the image is horizontol, then makes a square crop at left,
        center, right for 0, 1, 2 respectively
        """
        size = sz, sz
        if im.width == im.height:
            to_crop = False
        if to_crop:
            if crop_where == 0:
                if im.height > im.width:
                    im = im.crop((0, 0, im.width, im.width))
                else:
                    im = im.crop((0, 0, im.height, im.height))
            elif crop_where == 1:
                if im.height > im.width:
                    im = im.crop(
                        (
                            0,
                            im.height // 2 - im.width // 2,
                            im.width,
                            im.height // 2 + im.width // 2,
                        )
                    )
                else:
                    im = im.crop(
                        (
                            im.width // 2 - im.height // 2,
                            0,
                            im.width // 2 + im.height // 2,
                            im.height,
                        )
                    )
            elif crop_where == 2:
                if im.height > im.width:
                    im = im.crop((0, im.height - im.width, im.width, im.height))
                else:
                    im = im.crop((im.width - im.height, 0, im.width, im.height))
            else:
                raise ValueError(
                    "Wrong value for crop_where. 0, 1, 2 are valid values, read docstring."
                )
        else:
            pass

        im.thumbnail(size)
        if should_circle:
            im = ImageUtil.circumsize(im)
        return ImageUtil.pilImageToSurface(im)


class UberRect(pygame.Rect):
    def __init__(
        self,
        left: float,
        top: float,
        width: float,
        height: float,
        target: float,
        title: str,
        color: Color,
    ) -> None:
        super().__init__(left, top, width, height)
        self.target: float = target
        self.title: str = title
        self.color: Color = color

    def as_rect(self):
        return pygame.Rect(self.left, self.top, self.width, self.height)


class PyGamer:
    def __init__(self, dimensions: tuple[int, int]) -> None:
        pygame.init()
        self.running: bool = True
        self.aw, self.ah = (*dimensions,)
        self.screen: pygame.surface.Surface = pygame.display.set_mode(
            dimensions, pygame.NOFRAME
        )
        self.t0: float = 0.0
        self.time_elapsed: float = 0.0
        self.fpsClock = pygame.time.Clock()

    def draw_data_rects(
        self,
        data: list,
        header: pygame.Rect,
        header_color: Color,
        header_render,
        header_rend_rect,
    ):
        pygame.draw.rect(self.screen, header_color.rgb(), header)
        self.screen.blit(header_render, header_rend_rect)
        for i in data:
            pygame.draw.rect(self.screen, i.color.rgb(), i.as_rect())

    def draw_rect_text(
        self,
        data: list[tuple[pygame.surface.Surface, pygame.rect.Rect]],
        to_draw: list[bool],
    ):
        for item, draw in zip(data, to_draw):
            if draw:
                self.screen.blit(item[0], item[1])

    def draw_continuous_numbers(self, data):
        for render, rect, to_draw in data:
            if to_draw:
                self.screen.blit(render, rect)

    def draw_image_on_right(self, column, images: list, position_data):
        for im, obj in zip(images, position_data):
            if obj.width > 0:
                self.screen.blit(im, (obj.right - 5 + column * 40, obj.centery - 25))

    def kill_switch(self, event: pygame.event.EventType) -> None:  # type: ignore
        """Clicking quit button or pressing esc exits out the program."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            else:
                self.running = True
        else:
            self.running = True


class Graph:
    def __init__(
        self,
        pgapp: PyGamer,
        data: list[tuple[str, int]],
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
        self.data: list[tuple[str, int]] = data
        self.bars_count: int = len(data)
        self.header: pygame.Rect = pygame.Rect(0, 0, pgapp.aw, header)
        self.bar_height: int = bar_height
        self.width_multiplier: float = width_multiplier
        self.bars: list = list()
        self.gap: float = (
            self.pgapp.ah - self.header.height - (self.bars_count * bar_height)
        ) / (1 + self.bars_count)
        self.colors: list[Color] = colors
        self.left_gap = left_gap

        self.create_header(header_font, header_font_size, header_text)

        self.seed_rectangles()
        self.create_text_render(small_text_size, header_font, text_bar_distance)

    def create_header(self, header_font, header_font_size, header_text):
        self.header_font = pygame.font.Font(header_font, header_font_size)
        self.header_text_render = self.header_font.render(
            header_text, True, Color.rgb_white()
        )
        self.header_text_rect: pygame.rect.Rect = self.header_text_render.get_rect()
        self.header_text_rect.center = self.header.width // 2, self.header.height // 2

    def seed_rectangles(self):
        for idx, (k, v) in enumerate(self.data):
            self.bars.append(
                UberRect(
                    self.left_gap,
                    self.header.height + self.gap * (idx + 1) + self.bar_height * idx,
                    0,
                    self.bar_height,
                    v * self.width_multiplier,
                    k,
                    self.colors[idx],
                )
            )

    def create_text_render(self, font_size, header_font, extra_gap):
        self.store_rect_render: list[
            tuple[pygame.surface.Surface, pygame.rect.Rect]
        ] = list()
        # this needs to run before create_continuous_render since it creates the
        self.text_font_obj = pygame.font.Font(header_font, font_size)
        for idx, obj in enumerate(self.bars):
            render = self.text_font_obj.render(obj.title, True, Color.rgb_white())
            render_rect = render.get_rect()
            render_rect.center = (render_rect.center[0], obj.centery)
            render_rect.right = self.left_gap - extra_gap
            self.store_rect_render.append((render, render_rect))

    def simultaneous_grow(self, time_each):
        for item in self.bars:
            if item.width < item.target:
                item.width = self.increment_rect(
                    item.target, self.pgapp.time_elapsed, time_each
                )

    def top_down_grow(self, time_each):
        for idx, item in enumerate(self.bars):
            if item.width < item.target:
                item.width = self.increment_rect(
                    item.target, self.pgapp.time_elapsed - idx * time_each, time_each
                )

    def bottom_up_grow(self, time_each):
        for idx, item in enumerate(self.bars[::-1]):
            if item.width < item.target:
                item.width = self.increment_rect(
                    item.target, self.pgapp.time_elapsed - idx * time_each, time_each
                )

    def create_continuous_renders(
        self, gap_from_right, color: Color
    ) -> Iterator[tuple[pygame.surface.Surface, pygame.rect.Rect, bool]]:
        for obj in self.bars:
            render = self.text_font_obj.render(
                f"{str((obj.width // self.width_multiplier))}"
                if obj.width < obj.target
                else f"{str((obj.target//self.width_multiplier))}",
                True,
                color.rgb(),
            )
            render_rect: pygame.rect.Rect = render.get_rect()
            render_rect.right = obj.right - gap_from_right
            render_rect.centery = obj.centery
            yield render, render_rect, obj.width > gap_from_right + render_rect.width

    @staticmethod
    def increment_rect(target: float, deltat: float, time_each: float) -> int:
        increment_per_ms = target / (time_each * 100)
        return round(deltat * increment_per_ms * 100)

    @staticmethod
    def roundup(x) -> int:
        return int(math.ceil(x / 100.0)) * 100


if __name__ == "__main__":
    FONT: str = "./res/Kelvinch-Bold.otf"  # "./res/Shaky Hand Some Comic_bold.otf"
    TIME_EACH: float = 1
    FPS: int = 60
    TITLE: str = "20 Longest Running Animes of All Time"

    # the k_v_pair will contain the title of the bar and the total value of the bar in a k, v pair tuple
    # k_v_pair: list[tuple[str, int]] = []

    # to display the image on the right side, make a column of images of same length as k_v_pair,
    # the PIL.Image should have ImageUtil.get_images_ready to run on them to crop them and convert to pygame.Surface
    # a: list[pygame.Surface] = []

    # start doing data farm here
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
    # end doing data farm here

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
    app = PyGamer(SIZE)
    graph = Graph(
        pgapp=app,
        data=[i for i in k_v_pair],
        header=100,
        header_text=TITLE,
        header_font_size=69,
        header_font=FONT,
        bar_height=40,
        width_multiplier=1,
        colors=pastels,
        left_gap=550,
        text_bar_distance=30,
        small_text_size=30,
    )
    while app.running:
        app.t0 = time.time()
        for event in pygame.event.get():
            app.kill_switch(event)

        app.screen.fill(bg_color.rgb())
        graph.bottom_up_grow(TIME_EACH)
        app.draw_data_rects(
            graph.bars,
            graph.header,
            header_color,
            graph.header_text_render,
            graph.header_text_rect,
        )
        app.draw_rect_text(
            graph.store_rect_render, [bar.width > 0 for bar in graph.bars]
        )
        renders = graph.create_continuous_renders(10, bg_color)
        app.draw_continuous_numbers(renders)
        app.draw_image_on_right(0, a, graph.bars)
        app.draw_image_on_right(1, b, graph.bars)
        app.draw_image_on_right(2, c, graph.bars)
        app.draw_image_on_right(3, d, graph.bars)
        pygame.display.update()
        app.fpsClock.tick(FPS)
        app.time_elapsed += time.time() - app.t0
