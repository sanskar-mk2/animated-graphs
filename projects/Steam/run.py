from src.pg_app import PgApp
from src.graph import Graph, GraphConfig
from src.color import Color
import pandas as pd


def main():
    df = pd.read_csv("steam-insights/reviews.csv", on_bad_lines="skip")
    df["positive"] = pd.to_numeric(df["positive"], errors="coerce")
    df = df.sort_values("positive", ascending=False)
    k_v_pair = list(
        zip(df["app_id"].head(10).astype(str), df["positive"].head(10).astype(int))
    )
    print(k_v_pair)
    pgapp = PgApp((1920, 1080))
    config = GraphConfig(
        header_font="./src/assets/Arial.ttf",
        header_font_size=20,
        header_text="test",
        bar_height=80,
        width_multiplier=0.0005,
        colors=[Color("#FF0000"), Color("#00FF00"), Color("#0000FF")],
        left_gap=120,
        text_bar_distance=20,
        small_text_size=40,
        to_show=10,
        fps=60,
        animation_speed=0.5,
        bg_color=Color("#aaaaaa"),
        header_color=Color("#FFFFFF"),
        value_gap=10,
        animation_type="bottom_up",
    )
    graph = Graph(pgapp=pgapp, data=k_v_pair, header_height=100, config=config)
    graph.run()


if __name__ == "__main__":
    main()
