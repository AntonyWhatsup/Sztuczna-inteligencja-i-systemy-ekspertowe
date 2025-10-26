# panel.py

class Panel:
    def __init__(self, width: float, height: float, gap_x: float = 0, gap_y: float = 0):
        """
        width, height – розміри панелі (мм або м)
        gap_x, gap_y – відстань між панелями (мм або м)
        """
        self.width = width
        self.height = height
        self.gap_x = gap_x
        self.gap_y = gap_y


def fill_roof_with_panels(roof, panel):
    """Заповнює дах панелями з урахуванням відстаней між ними."""
    effective_width = panel.width + panel.gap_x
    effective_height = panel.height + panel.gap_y

    cols = int(roof.length // effective_width)
    rows = int(roof.width // effective_height)
    total_panels = cols * rows

    used_width = cols * panel.width + (cols - 1) * panel.gap_x
    used_height = rows * panel.height + (rows - 1) * panel.gap_y
    coverage = (used_width * used_height) / roof.area()

    return {
        "rows": rows,
        "cols": cols,
        "total_panels": total_panels,
        "coverage": coverage,
        "used_width": used_width,
        "used_height": used_height
    }
