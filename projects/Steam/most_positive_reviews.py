from src.pg_app import PgApp
from src.graph import Graph, GraphConfig
from src.color import Color
import pandas as pd
import os
import requests
import urllib.parse


def download_header_image(app_id, header_image_url, current_dir):
    # Create header_images directory if it doesn't exist
    header_images_dir = os.path.join(current_dir, "steam-insights/header_images")
    os.makedirs(header_images_dir, exist_ok=True)

    # Get file extension from URL
    parsed_url = urllib.parse.urlparse(header_image_url)
    extension = os.path.splitext(parsed_url.path)[1]
    if not extension:
        extension = ".jpg"  # Default to jpg if no extension found

    # Create filename
    filename = os.path.join(header_images_dir, f"{app_id}{extension}")

    # Check if file already exists (caching)
    if not os.path.exists(filename):
        try:
            response = requests.get(header_image_url)
            response.raise_for_status()
            with open(filename, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error downloading image for app_id {app_id}: {e}")

    return filename


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

    promotional_df = pd.read_csv(
        os.path.join(current_dir, "steam-insights/promotional.csv"),
        on_bad_lines="skip",
        dtype={
            "app_id": str,
            "header_image": str,
            "background_image": str,
            "screenshots": str,
            "movies": str,
        },
        encoding="utf-8",
        encoding_errors="ignore",
        quoting=1,
        escapechar="\\",
    )

    image_paths = []
    for i in range(len(id_positive_pair)):
        app_id = id_positive_pair[i][0]
        name = games_df[games_df["app_id"] == app_id]["name"].values[0]

        # Get and download header image
        header_image_url = promotional_df[promotional_df["app_id"] == app_id][
            "header_image"
        ].values[0]
        image_path = download_header_image(app_id, header_image_url, current_dir)
        image_paths.append(image_path)

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
        bg_color=Color("#eeeeee"),
        header_bg_color=Color("#6c5671"),
        header_text_color=Color("#ffffff"),
        value_gap=10,
        animation_type="bottom_up_flat",
        record_path="outputs/steam_most_positive_reviews.mp4",
        image_paths=image_paths,
    )
    graph = Graph(pgapp=pgapp, data=k_v_pair, header_height=100, config=config)
    graph.run()
