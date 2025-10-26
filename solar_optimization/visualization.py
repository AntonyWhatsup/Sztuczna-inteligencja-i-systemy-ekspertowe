# visualization.py

import matplotlib.pyplot as plt

def draw_roof(roof, panel, data):
    """Малює дах із розміщеними панелями та відстанями між ними."""
    fig, ax = plt.subplots()

    for i in range(data["rows"]):
        for j in range(data["cols"]):
            x = j * (panel.width + panel.gap_x)
            y = i * (panel.height + panel.gap_y)
            rect = plt.Rectangle(
                (x, y),
                panel.width,
                panel.height,
                edgecolor='blue',
                facecolor='skyblue',
                alpha=0.7
            )
            ax.add_patch(rect)

    ax.set_xlim(0, roof.length)
    ax.set_ylim(0, roof.width)
    ax.set_aspect('equal')
    plt.title("Rozmieszczenie paneli na dachu")
    plt.xlabel("Długość (mm)")
    plt.ylabel("Szerokość (mm)")
    plt.show()
