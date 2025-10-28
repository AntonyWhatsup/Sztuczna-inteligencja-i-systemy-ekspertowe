# formulas.py

def efficiency(panel_power, total_panels):
    """Obliczenie sumarycznej mocy systemu. (Обчислення сумарної потужності системи)."""
    return panel_power * total_panels


def cost(total_panels, cost_per_panel):
    """Ocena kosztu systemu. (Оцінка вартості системи)."""
    return total_panels * cost_per_panel