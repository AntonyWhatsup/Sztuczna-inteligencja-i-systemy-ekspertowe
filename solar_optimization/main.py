from config import POPULATION_SIZE, GENERATIONS, MUTATION_RATE
from evolution import evolve
from visualization import visualize_grid_layout

if __name__ == "__main__":
    print("Running grid-based evolutionary optimization...")
    results = evolve(POPULATION_SIZE, GENERATIONS, MUTATION_RATE)

    # pick best by energy - small cost penalty
    best = max(results, key=lambda r: r[1][0]-0.001*r[1][1])
    genome, angles = best[0]
    visualize_grid_layout(genome, angles, "best_grid_layout")

    print("Optimization finished. Check /results/ folder.")
