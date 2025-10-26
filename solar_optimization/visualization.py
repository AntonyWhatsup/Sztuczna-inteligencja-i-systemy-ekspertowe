# visualization.py

import matplotlib.pyplot as plt

def draw_roof(ax, roof, panel, data, offset_y=0, flip=False, title=""):
    """Малює одну площину даху з вертикальним зсувом, враховуючи відступи (border)."""
    
    start_x = data.get("border_x", 0)
    start_y = data.get("border_y", 0)

    for i in range(data["rows"]):
        for j in range(data["cols"]):
            x = start_x + j * (panel.width + panel.gap_x)
            y = start_y + i * (panel.height + panel.gap_y)
            
            if flip:
                # Y-координата відраховується від краю даху мінус (border + висота панелей + ряди панелей)
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

    ax.set_xlim(0, roof.length)
    ax.set_aspect('equal')
    ax.set_xlabel("Długość (mm)")
    ax.set_ylabel("Szerokość (mm)")

def draw_two_mirrored_roofs(roof_upper, roof_lower, panel, data_upper, data_lower, gap_between_planes=200):
    """
    Малює дзеркальні площини одна над одною, обидві додатні, з відліком від гребеня (0).
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # --- 1. Візуалізація площин ---
    red_line_y = roof_lower.width + gap_between_planes / 2 
    total_height = roof_upper.width + roof_lower.width + gap_between_planes 

    # Нижня площина
    offset_lower = 0
    draw_roof(ax, roof_lower, panel, data_lower, offset_y=offset_lower, flip=True)

    # Верхня площина
    offset_upper = roof_lower.width + gap_between_planes
    draw_roof(ax, roof_upper, panel, data_upper, offset_y=offset_upper, flip=True)

    # --- 2. Гребінь та Межі ---
    ax.axhline(y=red_line_y, color='red', linewidth=4, zorder=3)

    max_length = max(roof_upper.length, roof_lower.length)
    ax.set_ylim(0, total_height)
    ax.set_xlim(0, max_length)
    ax.set_aspect('equal')
    
    # --- 3. Налаштування подвійної осі Y (Ширина) ---

    all_ticks = []
    all_labels = []
    step = 1000

    # Мітки для НИЖНЬОЇ площини (від гребеня вниз)
    for i in range(int(roof_lower.width / step) + 1):
        tick_label = i * step
        tick_coord = red_line_y - tick_label
        if tick_coord >= 0:
            all_ticks.append(tick_coord)
            all_labels.append(f"{tick_label:.0f}")
            
    # Додаємо мітку для повної ширини (5500)
    if roof_lower.width % step != 0:
        edge_coord = red_line_y - roof_lower.width
        if edge_coord >= 0:
            all_ticks.append(edge_coord)
            all_labels.append(f"{roof_lower.width:.0f}")


    # Мітки для ВЕРХНЬОЇ площини (від гребеня вгору)
    for i in range(1, int(roof_upper.width / step) + 1):
        tick_label = i * step
        tick_coord = red_line_y + tick_label
        if tick_coord <= total_height:
            all_ticks.append(tick_coord)
            all_labels.append(f"{tick_label:.0f}")

    # Додаємо мітку для повної ширини (5500)
    if roof_upper.width % step != 0:
        edge_coord = red_line_y + roof_upper.width
        if edge_coord <= total_height:
            all_ticks.append(edge_coord)
            all_labels.append(f"{roof_upper.width:.0f}")

    # Об'єднання, усунення дублікатів та сортування міток
    unique_ticks = {}
    for t, l in zip(all_ticks, all_labels):
        unique_ticks[t] = l
    
    all_ticks_sorted = sorted(unique_ticks.keys())
    all_labels_sorted = [unique_ticks[t] for t in all_ticks_sorted]
    
    ax.set_yticks(all_ticks_sorted)
    ax.set_yticklabels(all_labels_sorted)
    
    ax.set_title("Dwuspadowy dach - dwie lustrzane powierzchnie (Відлік від гребеня)")
    ax.set_xlabel("Długość (mm)")
    ax.set_ylabel("Ширина (мм) - Відлік від гребеня (0)")

    # Позначка гребеня
    ax.text(-max_length * 0.02, red_line_y, "ГРЕБІНЬ (0)", color='red', va='center', ha='right', fontsize=12, fontweight='bold', zorder=4)

    plt.grid(True, linestyle="--", alpha=0.5, zorder=1) 
    plt.tight_layout()
    plt.show()