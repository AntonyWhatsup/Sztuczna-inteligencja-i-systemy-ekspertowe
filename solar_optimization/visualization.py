# visualization.py
import matplotlib.pyplot as plt

def draw_roof(ax, roof, panel, data, offset_y=0, flip=False):
    """Малює одну площину даху."""
    start_x = data.get("border_x", 0)
    start_y = data.get("border_y", 0)

    for i in range(data["rows"]):
        for j in range(data["cols"]):
            x = start_x + j * (panel.width + panel.gap_x)
            y = start_y + i * (panel.height + panel.gap_y)

            if flip:
                # Дзеркально для верхньої площини
                y = roof.width - (start_y + i * (panel.height + panel.gap_y) + panel.height)

            y += offset_y
            rect = plt.Rectangle(
                (x, y),
                panel.width,
                panel.height,
                edgecolor='blue',
                facecolor='skyblue',
                alpha=0.7,
                zorder=2
            )
            ax.add_patch(rect)


def draw_two_mirrored_roofs(roof_upper, roof_lower, panel, data_upper, data_lower, border=0, gap_between_planes=200):
    """
    Малює дві дзеркальні площини, розділені червоною лінією (гребенем),
    яка є точкою відліку (0). В обох напрямках (вгору і вниз) координати додатні.
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # --- Конфігурація ---
    red_line_y = roof_lower.width + gap_between_planes / 2  # гребінь посередині
    total_height = roof_upper.width + roof_lower.width + gap_between_planes
    max_length = max(roof_upper.length, roof_lower.length)

    # --- Нижня площина ---
    # Відлік іде вниз від гребеня, але координати залишаються додатними
    offset_lower = 0
    draw_roof(ax, roof_lower, panel, data_lower, offset_y=offset_lower, flip=False)

    # --- Верхня площина ---
    offset_upper = roof_lower.width + gap_between_planes
    draw_roof(ax, roof_upper, panel, data_upper, offset_y=offset_upper, flip=True)

    # --- Червона лінія (нуль) ---
    ax.axhline(y=red_line_y, color='red', linewidth=3, zorder=3)
    ax.text(-max_length * 0.02, red_line_y, "0 (ГРЕБІНЬ)", color='red',
            va='center', ha='right', fontsize=12, fontweight='bold')

    # --- Формування подвійної осі Y ---
    all_ticks, all_labels = [], []
    step = 1000

    # Вниз від гребеня (нижня площина)
    for i in range(0, int(roof_lower.width / step) + 1):
        tick = red_line_y - i * step
        if tick >= 0:
            all_ticks.append(tick)
            all_labels.append(f"{i*step}")

    # Вгору від гребеня (верхня площина)
    for i in range(1, int(roof_upper.width / step) + 1):
        tick = red_line_y + i * step
        if tick <= total_height:
            all_ticks.append(tick)
            all_labels.append(f"{i*step}")

    ax.set_yticks(all_ticks)
    ax.set_yticklabels(all_labels)

    # --- Межі графіка ---
    ax.set_xlim(-border / 2, max_length + border / 2)
    ax.set_ylim(0, total_height)
    ax.set_aspect('equal')

    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_title("Dwuspadowy dach — Відлік від гребеня (0) в обидва боки")
    ax.set_xlabel("Długość (mm)")
    ax.set_ylabel("Відстань від гребеня (мм)")

    plt.tight_layout()
    plt.show()
