def efficiency(panel_power, total_panels):
    """Calculate the total power output of the system."""
    return panel_power * total_panels


def cost(total_panels, cost_per_panel):
    """Estimate the total cost of the solar system."""
    return total_panels * cost_per_panel
