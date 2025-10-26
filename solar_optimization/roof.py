# roof.py

class Roof:
    def __init__(self, width: float, length: float):
        """
        width, length – розміри даху (мм або м)
        """
        self.width = width
        self.length = length

    def area(self) -> float:
        """Повертає площу даху."""
        return self.width * self.length
