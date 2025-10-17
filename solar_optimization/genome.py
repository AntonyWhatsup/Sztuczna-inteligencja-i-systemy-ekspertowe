import numpy as np
import random
from config import GRID_ROWS, GRID_COLS, TILT_ANGLES

def random_genome(max_panels=10):
    """Generate a random genome on grid: 2D array for panels and angles."""
    genome = np.zeros((GRID_ROWS, GRID_COLS), dtype=int)
    angles = np.zeros((GRID_ROWS, GRID_COLS), dtype=int)

    num_panels = min(max_panels, GRID_ROWS*GRID_COLS)
    positions = random.sample([(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)], num_panels)

    for r, c in positions:
        genome[r, c] = 1
        angles[r, c] = random.choice(TILT_ANGLES)

    return genome, angles

def mutate(genome, angles):
    """Move a random panel to a neighboring empty cell or change its tilt."""
    rows, cols = genome.shape
    new_genome = genome.copy()
    new_angles = angles.copy()

    panel_positions = [(r, c) for r in range(rows) for c in range(cols) if genome[r, c] == 1]
    if not panel_positions:
        return new_genome, new_angles

    r, c = random.choice(panel_positions)

    # 50% chance to move, 50% chance to change tilt
    if random.random() < 0.5:
        # move to a random empty neighbor
        neighbors = [(r+dr, c+dc) for dr in [-1,0,1] for dc in [-1,0,1]
                     if 0<=r+dr<rows and 0<=c+dc<cols and new_genome[r+dr, c+dc]==0]
        if neighbors:
            r2, c2 = random.choice(neighbors)
            new_genome[r, c] = 0
            new_genome[r2, c2] = 1
            new_angles[r2, c2] = new_angles[r, c]
            new_angles[r, c] = 0
    else:
        new_angles[r, c] = random.choice(TILT_ANGLES)

    return new_genome, new_angles
