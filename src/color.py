import random


class Color:
    def __init__(self, color) -> None:
        """Initialize a Color object from a hex string or RGB(A) tuple.

        Args:
            color: Either a hex string (with or without #) or RGB(A) tuple

        Raises:
            ValueError: If tuple has wrong number of values
            TypeError: If color arg is not string or tuple
        """
        if isinstance(color, tuple):
            if len(color) == 3:
                self.r, self.g, self.b = color
                self.a = None
            elif len(color) == 4:
                self.r, self.g, self.b, self.a = color
            else:
                raise ValueError("Need three or four values in tuples only.")
        elif isinstance(color, str):
            if color.startswith("#"):
                color = color[1:]
            if len(color) == 6:
                self.r = int(color[0:2], 16)
                self.g = int(color[2:4], 16)
                self.b = int(color[4:6], 16)
                self.a = None
            elif len(color) == 8:
                self.r = int(color[0:2], 16)
                self.g = int(color[2:4], 16)
                self.b = int(color[4:6], 16)
                self.a = int(color[6:8], 16)
            else:
                raise ValueError("Hex string must be 6 or 8 characters")
        else:
            raise TypeError("Only pass hex as string or RGB(A) tuples.")

    def __repr__(self) -> str:
        """Return string representation of color values."""
        return f"Color{self.rgba()}"

    def rgb(self) -> tuple:
        """Return RGB values as tuple."""
        return self.r, self.g, self.b

    def rgba(self) -> tuple:
        """Return RGBA values as tuple, omitting alpha if not set."""
        return (
            (self.r, self.g, self.b, self.a)
            if self.a is not None
            else (self.r, self.g, self.b)
        )

    @staticmethod
    def random_rgb(start: int = 0, end: int = 255) -> "Color":
        """Generate a random RGB color within given range.

        Args:
            start: Min value for RGB components (default 0)
            end: Max value for RGB components (default 255)

        Returns:
            New Color instance with random RGB values
        """
        return Color(
            (
                random.randint(start, end),
                random.randint(start, end),
                random.randint(start, end),
            )
        )

    @staticmethod
    def rgb_black() -> tuple:
        """Return RGB values for black."""
        return Color("#000000").rgb()

    @staticmethod
    def rgb_white() -> tuple:
        """Return RGB values for white."""
        return Color("#ffffff").rgb()
