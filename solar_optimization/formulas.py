# formulas.py

def efficiency(panel_power, total_panels):
    """Обчислення сумарної потужності системи."""
    return panel_power * total_panels


def cost(total_panels, cost_per_panel):
    """Оцінка вартості системи."""
    return total_panels * cost_per_panel
