from config import PANEL_COST

def evaluate(genome, angles):
    """
    Evaluate a genome: returns (energy, cost, shadow)
    - Energy: sum of panels * (1 + tilt/45)
    - Cost: number of panels * PANEL_COST
    - Shadow: number of panels * 0.2 (fake overlap penalty)
    """
    num_panels = genome.sum()
    cost = num_panels * PANEL_COST

    energy = sum((1 + angles[r,c]/45)*1000
                 for r in range(genome.shape[0])
                 for c in range(genome.shape[1]) if genome[r,c]==1)

    shadow = num_panels * 0.2

    return energy, cost, shadow
