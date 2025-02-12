from src.color import Color
from projects.PYPL.pypl_data_loader import load_data
from src.animated_graph import PygameExtended
from src.graph import GraphConfig
from src.animated_graph import BarChartAnimation


visualization_data = load_data("./PYPL/IN.json")

WINDOW_SIZE = (1920, 1080)
app = PygameExtended(WINDOW_SIZE)

# Configure visualization
chart_config = GraphConfig(
    header_font="./assets/fonts/Arial.ttf",
    header_font_size=69,
    header_text="Popularity of Programming Language (India)",
    bar_height=40,
    width_multiplier=100,
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
    animation_speed=0.1,
    bg_color=Color("#28282e"),
    header_bg_color=Color("#6c5671"),
    header_text_color=Color("#ffffff"),
    value_gap=10,
    record_path="outputs/pypl_pypl_india_graph.mp4",
    wait_time_after_completion=3,
    value_prepost=("~", "%"),
)

# Create and run visualization
chart = BarChartAnimation(
    pygame_app=app,
    chart_data=visualization_data,
    header_height=100,
    chart_config=chart_config,
)
chart.run()
