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


def fill_roof_with_panels(roof, panel, border_x: float = 0, border_y: float = 0):
    """
    Заповнює дах панелями з урахуванням відстаней між ними та відступів від країв.
    border_x, border_y - мінімальний відступ від усіх 4 країв даху.
    """
    
    # Фактична доступна площа даху для розміщення панелей
    available_length = roof.length - 2 * border_x
    available_width = roof.width - 2 * border_y

    effective_width = panel.width + panel.gap_x
    effective_height = panel.height + panel.gap_y

    cols = int(available_length // effective_width)
    rows = int(available_width // effective_height)
    
    if cols < 0: cols = 0
    if rows < 0: rows = 0
        
    total_panels = cols * rows

    if cols > 0:
        used_width_panels = cols * panel.width + (cols - 1) * panel.gap_x
        used_width = used_width_panels + 2 * border_x
    else:
        used_width = 0

    if rows > 0:
        used_height_panels = rows * panel.height + (rows - 1) * panel.gap_y
        used_height = used_height_panels + 2 * border_y
    else:
        used_height = 0

    coverage = (used_width * used_height) / roof.area() if roof.area() > 0 else 0

    return {
        "rows": rows,
        "cols": cols,
        "total_panels": total_panels,
        "coverage": coverage,
        "used_width": used_width,
        "used_height": used_height,
        "border_x": border_x, 
        "border_y": border_y
    }