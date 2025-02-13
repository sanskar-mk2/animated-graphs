from src.pg_app import PgApp
from src.graph import Graph, GraphConfig
from src.color import Color
import pandas as pd
import os


def main():
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    df = pd.read_csv(
        os.path.join(current_dir, "steam-insights/reviews.csv"),
        on_bad_lines="skip",
        na_values=["\\N", "N"],
        dtype={
            "app_id": str,
            "review_score": "Int64",
            "review_score_description": str,
            "positive": "Int64",
            "negative": "Int64",
            "total": "Int64",
            "metacritic_score": str,
            "reviews": str,
            "recommendations": str,
            "steamspy_user_score": str,
            "steamspy_score_rank": str,
            "steamspy_positive": str,
            "steamspy_negative": str,
        },
        encoding="utf-8",
        encoding_errors="ignore",
        quoting=1,  # QUOTE_ALL to handle embedded quotes and HTML
        escapechar="\\",  # Add escape character for embedded quotes
    )
    df["positive"] = pd.to_numeric(df["positive"], errors="coerce")
    df = df.sort_values("positive", ascending=False)
    id_positive_pair = list(
        zip(
            df["app_id"].head(10).astype(str),
            df["positive"].head(10).astype(int),
        )
    )
    k_v_pair = []
    games_df = pd.read_csv(
        os.path.join(current_dir, "steam-insights/games.csv"),
        on_bad_lines="skip",
        dtype={
            "app_id": str,
            "name": str,
            "release_date": str,
            "is_free": str,
            "price_overview": str,
            "languages": str,
            "type": str,
        },
        encoding="utf-8",
        encoding_errors="ignore",
        quoting=1,
        escapechar="\\",
    )

    for i in range(len(id_positive_pair)):
        name = games_df[games_df["app_id"] == id_positive_pair[i][0]]["name"].values[0]
        k_v_pair.append((name, id_positive_pair[i][1]))

    pgapp = PgApp((1920, 1080))
    config = GraphConfig(
        header_font="./assets/fonts/Arial.ttf",
        header_font_size=40,
        header_text="Steam games with most positive reviews",
        bar_height=80,
        width_multiplier=0.0005,
        colors=[
            Color("#00b6db"),
            Color("#00db6d"),
            Color("#ffb600"),
            Color("#ff926d"),
            Color("#db0000"),
            Color("#dbdbdb"),
        ],
        left_gap=120,
        text_bar_distance=20,
        small_text_size=40,
        to_show=10,
        fps=60,
        animation_speed=1,
        bg_color=Color("#000000"),
        header_bg_color=Color("#FFFFFF"),
        header_text_color=Color("#000000"),
        value_gap=10,
        animation_type="simultaneous_flat",
        record_path="",
    )
    graph = Graph(pgapp=pgapp, data=k_v_pair, header_height=100, config=config)
    graph.run()
