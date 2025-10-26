# visualization.py

import matplotlib.pyplot as plt

def draw_roof(ax, roof, panel, data, offset_y=0, flip=False, title=""):
    """Малює одну площину даху з вертикальним зсувом.
       flip=True перевертає площину вниз від осі Y=0.
    """
    for i in range(data["rows"]):
        for j in range(data["cols"]):
            x = j * (panel.width + panel.gap_x)
            y = i * (panel.height + panel.gap_y)
            if flip:
                y = -y - panel.height  # перевертаємо вниз від нуля
            y += offset_y
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
    ax.set_aspect('equal')
    ax.set_title(title)
    ax.set_xlabel("Długość (mm)")
    ax.set_ylabel("Szerokość (mm)")

def draw_two_separate_roofs(roof_left, roof_right, panel, data_left, data_right, gap_between_planes=200):
    """
    Малює дві площини дзеркально від центральної осі Y=0.
    gap_between_planes - відстань між верхньою та нижньою площинами (мм)
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # Верхня площина (Y↑)
    draw_roof(ax, roof_left, panel, data_left, offset_y=gap_between_planes/2, flip=False, title="Górny skos dachu")

    # Нижня площина (Y↓)
    draw_roof(ax, roof_right, panel, data_right, offset_y=-gap_between_planes/2, flip=True, title="Dolny skos dachu")

    # Межі графіка
    total_height = roof_left.width + roof_right.width + gap_between_planes
    ax.set_ylim(-total_height/2, total_height/2)
    ax.set_xlim(0, max(roof_left.length, roof_right.length))
    ax.set_aspect('equal')

    # Товста лінія розмежування
    ax.axhline(y=0, color='red', linewidth=4)

    plt.title("Dwuspadowy dach - dwie powierzchnie lustrzane z przerwą")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()
