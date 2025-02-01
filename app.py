from pygameapp_rewrite_animated import AnimatedGraph, PyGamerExt
from color import Color
import pandas as pd  # type: ignore
import time
import pygame
from projects.All import arr_to_df, json_to_arr  # type: ignore

FONT: str = "./assets/fonts/Kelvinch-Bold.otf"
TIME_EACH: float = 0.1
FPS: int = 60
TITLE: str = "Programming Language Popularity"
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
    # data cleaning
    df = arr_to_df(json_to_arr("./projects/PYPL/All.json"))
    df = df * 100
    df = df.transpose()
    colname = df.columns.to_series()
    dates = pd.to_datetime(colname)
    datesstr = dates.dt.strftime("%b %Y")
    df.columns = datesstr

    # objects
    app: PyGamerExt = PyGamerExt(SIZE)
    graph: AnimatedGraph = AnimatedGraph(
        pgapp=app,
        data=df,
        header=100,
        header_text=TITLE,
        header_font_size=69,
        header_font=FONT,
        bar_height=40,
        width_multiplier=48,
        colors=pastels,
        left_gap=250,
        text_bar_distance=30,
        small_text_size=30,
        to_show=10,
        value_prepost=("~", "%"),
        # debug=True
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
        app.draw_rect_text(graph.data, [True for _ in graph.bars])
        renders = graph.create_continuous_renders(10, bg_color)
        dt_renders = graph.dt_renders("BR", Color("#ffffff"), 200)
        app.draw_dt(dt_renders)
        app.draw_continuous_numbers(renders)
        app.update_display()
        app.fpsClock.tick(FPS)
        app.time_elapsed += time.time() - app.t0
