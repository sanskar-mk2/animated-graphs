from pygame import Rect
from color import Color


class SuperRect(Rect):
    """A rectangle with additional properties for target value, title and color."""

    def __init__(
        self,
        left: float,
        top: float,
        width: float,
        height: float,
        target: float,
        title: str,
        color: Color,
    ) -> None:
        """Initialize a SuperRect.

        Args:
            left: X coordinate of top left corner
            top: Y coordinate of top left corner
            width: Width of rectangle
            height: Height of rectangle
            target: Target value associated with this rectangle
            title: Title text for the rectangle
            color: Color object for rectangle fill color
        """
        super().__init__(left, top, width, height)
        self.target: float = target
        self.title: str = title
        self.color: Color = color

    def as_rect(self) -> Rect:
        """Convert to a basic Pygame Rect.

        Returns:
            A Pygame Rect with the same position and dimensions
        """
        return Rect(self.left, self.top, self.width, self.height)
