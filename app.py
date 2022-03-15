from pygameapp_rewrite_animated import AnimatedGraph, PyGamerExt
from color import Color
import numpy as np
import pandas as pd  # type: ignore
import time
import pygame
from projects.All import arr_to_df, json_to_arr  # type: ignore

FONT: str = "./assets/fonts/Kelvinch-Bold.otf"
TIME_EACH: float = 0.5
FPS: int = 60
TITLE: str = "Test Title"
pastels: list[Color] = [
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
bg_color: Color = Color("#28282e")
header_color: Color = Color("#6c5671")
SIZE: tuple[int, int] = 1920, 1080

if __name__ == "__main__":
    # create dummy data
    # keys = map(
    #     lambda x: chr(int(x * 26) + 97) * np.random.randint(3, 10), np.random.rand(10)
    # )
    # v0 = map(lambda x: int(x * 10) + 1, np.random.rand(10))
    # kv_dict: dict = dict()
    # keys_lst = [i for i in keys]
    # v0_lst = [i for i in v0]
    # for i in range(20):
    #     kv_dict.update({i: {}})
    #     for idx, k in enumerate(keys_lst):
    #         kv_dict[i].update({k: v0_lst[idx]})
    #     v0_lst = [a + np.random.randint(0, 10) for a in v0_lst]
    # df = pd.DataFrame(kv_dict)
    df = arr_to_df(json_to_arr("./projects/PYPL/All.json"))
    df = df * 100
    df = df.transpose()

    # objects
    app: PyGamerExt = PyGamerExt(SIZE)
    graph: AnimatedGraph = AnimatedGraph(
        pgapp=app,
        data=df,
        header=100,
        header_text=TITLE,
        header_font_size=69,
        header_font=FONT,
        bar_height=28,
        width_multiplier=10,
        colors=pastels,
        left_gap=250,
        text_bar_distance=30,
        small_text_size=30,
    )

    # main loop
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
        app.update_display()
        app.fpsClock.tick(FPS)
        app.time_elapsed += time.time() - app.t0
