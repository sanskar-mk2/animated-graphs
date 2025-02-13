# Animated Graphs

A Python library for creating smooth, animated bar chart visualizations using Pygame. This project allows you to create dynamic racing bar charts with customizable colors, animations, and recording capabilities.

## Features

-   Smooth bar animations with multiple animation styles
-   Customizable colors, fonts, and dimensions
-   Support for different animation types (bottom-up, top-down, simultaneous)
-   Video recording capabilities
-   Header and value label customization
-   Support for image integration with dominant color extraction
-   Flexible configuration options

## Installation

1. Clone the repository:

```bash
git clone https://github.com/sanskar-mk2/animated-graphs.git
cd animated-graphs
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Ensure you have the required assets:
    - Fonts in `./assets/fonts/`
    - Data files in appropriate directories

## Usage

Here's a basic example of how to use the library:

```python
from src.color import Color
from projects.PYPL.pypl_data_loader import load_data
from src.animated_graph import PygameExtended
from src.graph import GraphConfig
from src.animated_graph import BarChartAnimation

# Load your data
visualization_data = load_data("./ODE/All.json")

# Configure window
WINDOW_SIZE = (1920, 1080)
app = PygameExtended(WINDOW_SIZE)

# Set up configuration
chart_config = GraphConfig(
    header_font="./assets/fonts/Arial.ttf",
    header_font_size=69,
    header_text="Online IDE Popularity (Global)",
    bar_height=40,
    width_multiplier=100,
    colors=[
        Color("#f98284"),  # Red
        Color("#ffc384"),  # Orange
        # ... add more colors as needed
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
    record_path="outputs/animation.mp4",
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
```

## Example Outputs

Here are some example animations created with this library:

https://github.com/sanskar-mk2/animated-graphs/raw/main/outputs/h264/steam_most_positive_reviews.mp4
https://github.com/sanskar-mk2/animated-graphs/raw/main/outputs/h264/pypl_pypl_all_graph.mp4

## Configuration Options

### GraphConfig Parameters

-   `header_font`: Path to font file for header text
-   `header_font_size`: Font size for header text
-   `header_text`: Text to display in header
-   `bar_height`: Height of each bar in pixels
-   `width_multiplier`: Scale factor for bar widths
-   `colors`: List of Color objects for bars
-   `left_gap`: Space between left edge and bars
-   `text_bar_distance`: Space between text and bars
-   `small_text_size`: Font size for bar labels
-   `to_show`: Number of bars to display
-   `fps`: Frames per second for animation
-   `animation_speed`: Time in seconds for each bar's growth
-   `bg_color`: Background color
-   `header_bg_color`: Header background color
-   `header_text_color`: Header text color
-   `value_gap`: Gap between value text and bar edge
-   `record_path`: Path to save the recording
-   `wait_time_after_completion`: Time to wait after completion
-   `value_prepost`: Tuple of (prefix, suffix) for values
