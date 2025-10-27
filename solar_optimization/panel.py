# panel.py
import math

class Panel:
    """Модель сонячної панелі."""
    def __init__(self, width, height, gap_x=0, gap_y=0):
        self.width = width
        self.height = height
        self.gap_x = gap_x
        self.gap_y = gap_y


def fill_roof_with_panels(roof, panel, border_x=0, border_y=0):
    """Заповнення площини панелями з урахуванням відступів."""
    
    # Ефективна площа для панелей
    usable_length = roof.length - 2 * border_x
    usable_width = roof.width - 2 * border_y

    if usable_length <= 0 or usable_width <= 0:
        return {"rows": 0, "cols": 0, "total_panels": 0, "coverage": 0, 
                "border_x": border_x, "border_y": border_y}

    # Кількість панелей, які вміщуються
    cols = math.floor((usable_length + panel.gap_x) / (panel.width + panel.gap_x))
    rows = math.floor((usable_width + panel.gap_y) / (panel.height + panel.gap_y))

    total_panels = rows * cols

    # Площа панелей
    panel_area = panel.width * panel.height * total_panels
    roof_area = roof.width * roof.length
    coverage = panel_area / roof_area

    return {
        "rows": rows,
        "cols": cols,
        "total_panels": total_panels,
        "coverage": coverage,
        "border_x": border_x,
        "border_y": border_y
    }
