from pg_app import PgApp
from graph import Graph, GraphConfig
from color import Color

DATA = [
    ("Counter-Strike 2", 7271193),
    ("Dota 2", 1910300),
    ("PUBG: BATTLEGROUNDS", 1440190),
    ("Terraria", 1306503),
    ("Tom Clancy's Rainbow Six® Siege", 1123316),
    ("Garry's Mod", 1068744),
    ("Team Fortress 2", 990978),
    ("Rust", 972209),
    ("Black Myth: Wukong", 911343),
    ("ELDEN RING", 902340),
]
pgapp = PgApp((1920, 1080))
config = GraphConfig(
    header_font="./Arial.ttf",
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
    record_path="steam_games_positive_reviews.mp4",
)
graph = Graph(pgapp=pgapp, data=DATA, header_height=100, config=config)
graph.run()
