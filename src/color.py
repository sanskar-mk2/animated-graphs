import random


class Color:
    def __init__(self, color) -> None:
        if isinstance(color, tuple):
            if len(color) == 3:
                self.r = color[0]
                self.g = color[1]
                self.b = color[2]
                self.a = None
            elif len(color) == 4:
                self.r = color[0]
                self.g = color[1]
                self.b = color[2]
                self.a = color[3]
            else:
                raise ValueError("Need three or four value in tuples only.")
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
            raise TypeError("Only pass hex as string or rgb(a) tuples.")

    def __repr__(self) -> str:
        return f"{self.rgba()}"

    def rgb(self):
        return self.r, self.g, self.b

    def rgba(self):
        return (self.r, self.g, self.b, self.a) if self.a else (self.r, self.g, self.b)

    @staticmethod
    def random_rgb(start=None, end=None):
        if not start:
            start = 0
        if not end:
            end = 255
        return Color(
            (
                random.randint(start, end),
                random.randint(start, end),
                random.randint(start, end),
            )
        )

    @staticmethod
    def rgb_black():
        return Color("#000000").rgb()

    @staticmethod
    def rgb_white():
        return Color("#ffffff").rgb()

if __name__ == "__main__":
    print(Color.random_rgb())
