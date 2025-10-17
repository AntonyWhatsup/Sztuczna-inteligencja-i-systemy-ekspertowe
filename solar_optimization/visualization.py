import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

def plot_pareto(results):
    energies = [r[1][0] for r in results]
    costs = [r[1][1] for r in results]
    shadows = [r[1][2] for r in results]

    plt.figure()
    plt.scatter(costs, energies, c=shadows, cmap="viridis")
    plt.xlabel("Cost (PLN)")
    plt.ylabel("Annual Energy (kWh)")
    plt.colorbar(label="Shadow (%)")
    plt.title("Pareto Front")
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/pareto.png")
    plt.close()

def visualize_grid_layout(genome, angles, filename):
    rows, cols = genome.shape
    PANEL_WIDTH = 1
    PANEL_HEIGHT = 1

    plt.figure(figsize=(cols, rows))
    ax = plt.gca()
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_facecolor("#e0e0e0")
    ax.set_aspect('equal')
    plt.title("Solar Panel Layout (Grid)", fontsize=14, weight="bold")
    plt.xlabel("Columns")
    plt.ylabel("Rows")

    for r in range(rows):
        for c in range(cols):
            if genome[r, c] == 1:
                angle = angles[r, c]
                color = {
                    0: "#f9a825",
                    15: "#fbc02d",
                    30: "#fdd835",
                    45: "#ffee58"
                }.get(angle, "orange")
                rect = Rectangle((c, rows-r-1), PANEL_WIDTH, PANEL_HEIGHT, color=color, alpha=0.8, ec="black")
                ax.add_patch(rect)

    legend_handles = [
        Rectangle((0,0),1,1,color="#f9a825",label="0°"),
        Rectangle((0,0),1,1,color="#fbc02d",label="15°"),
        Rectangle((0,0),1,1,color="#fdd835",label="30°"),
        Rectangle((0,0),1,1,color="#ffee58",label="45°"),
    ]
    ax.legend(handles=legend_handles, title="Tilt Angle", loc="upper right")

    os.makedirs("results/layouts", exist_ok=True)
    plt.tight_layout()
    plt.savefig(f"results/layouts/{filename}.png", dpi=150)
    plt.close()
