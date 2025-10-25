# visualization.py - ФІНАЛЬНА ВЕРСІЯ: ПРЯМОКУТНІ ПАНЕЛІ ТА СЕКТОРИ З ВІДСТУПАМИ

import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
# FancyBboxPatch та Circle видалені, оскільки більше не потрібні

# ---------- 1) PARETO FRONT (стоимость ↔ энергия) ----------
def plot_pareto_front(results, filename="pareto_front.png"):
    """
    results: list of tuples (genome, (energy, cost, shadow))
    """
    energies = [r[1][0] for r in results]
    costs    = [r[1][1] for r in results]
    shadows  = [r[1][2] for r in results]

    plt.figure()
    plt.scatter(costs, energies, c=shadows, cmap="viridis")
    plt.xlabel("Cost (PLN)")
    plt.ylabel("Annual Energy (kWh)")
    cbar = plt.colorbar(label="Shadow (%)")
    plt.title("Pareto Front: Cost vs Energy")

    os.makedirs("results", exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join("results", filename), dpi=150)
    plt.close()

# --- Backward-compat shim ---
def plot_pareto(results):
    return plot_pareto_front(results, filename="pareto.png")

# ---------- 2) PARETO CHART (столбцы + кумулятив) ----------
# Залишаємо без змін
def plot_pareto_chart(contrib: dict, title="Pareto Chart", unit="PLN", filename="pareto_chart.png"):
    """
    contrib: dict {категория: вклад} — будет отсортирован по убыванию.
    """
    items = sorted(contrib.items(), key=lambda kv: kv[1], reverse=True)
    labels = [k for k, _ in items]
    vals   = [v for _, v in items]
    total  = sum(vals) if vals else 1.0
    cum    = [100 * sum(vals[:i+1]) / total for i in range(len(vals))]

    fig, ax = plt.subplots()
    ax.bar(range(len(vals)), vals)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel(unit)
    ax.set_title(title)

    ax2 = ax.twinx()
    ax2.plot(range(len(cum)), cum, marker="o")
    ax2.set_ylabel("CF %")
    ax2.set_ylim(0, 100)
    ax2.axhline(80, linestyle="--")

    for i, v in enumerate(cum):
        ax2.text(i, v, f"{v:.0f}%", va="bottom", ha="center", fontsize=8)

    os.makedirs("results", exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join("results", filename), dpi=150)
    plt.close()

# ---------- 3) ІКОНКА МОДУЛЯ (Прямокутна, без скруглень) ----------
def _draw_module_icon(
    ax, x, y, w, h,
    cell_rows=12, cell_cols=4,
    angle_label=None
):
    """
    Малює прямокутний модуль із сіткою ячейок та білим текстом кута нахилу.
    Панель не має скруглень.
    """
    # Основний прямокутник модуля (темно-сірий фон, що імітує рамку)
    ax.add_patch(Rectangle((x, y), w, h,
                           linewidth=1.0, edgecolor="black", facecolor="#424242", zorder=1))

    # Внутрішня область
    margin = 0.04 * min(w, h)
    gx, gy = x + margin, y + margin
    gw, gh = w - 2 * margin, h - 2 * margin

    # Сетка ячеек: ТЕМНО-СИНІ прямокутники
    gap = 0.08
    dx, dy = gw / cell_cols, gh / cell_rows
    pad_x, pad_y = dx * gap, dy * gap
    for r_i in range(cell_rows):
        for c_i in range(cell_cols):
            cx = gx + c_i * dx + pad_x/2
            cy = gy + r_i * dy + pad_y/2
            
            # Колір ячейки
            cell_color = "#1565C0" 
            
            ax.add_patch(Rectangle((cx, cy), dx - pad_x, dy - pad_y,
                                   facecolor=cell_color, edgecolor="#64B5F6", linewidth=0.1, zorder=2))

    # Білий, жирний текст кута нахилу
    if angle_label is not None:
        text_x = x + w/2
        text_y = y + margin + (gh / cell_rows * 0.5) # Позиціонуємо у верхній частині панелі, ближче до краю
        
        # Додаємо тінь або контрастний обвід для читабельності
        ax.text(text_x + 0.005, text_y + 0.005, f"{angle_label}°", 
                ha="center", va="center", fontsize=8, color='black', weight='bold', zorder=3, alpha=0.5) # Тінь
        
        # Основний білий текст
        ax.text(text_x, text_y, f"{angle_label}°", 
                ha="center", va="center", fontsize=8, color='white', weight='bold', zorder=4)

# ---------- 4) ПЛАН КРЫШИ (Прямокутний, з відступами) ----------
def visualize_grid_layout(genome, angles, filename,
                             cell_width_ratio=1.0,  # Ширина сектору сітки (залишаємо 1.0)
                             cell_height_ratio=2.0, # Висота сектору сітки (збільшуємо до 2.0 для прямокутника)
                             panel_aspect=2.3,      # Висота/ширина панелі (залишаємо 2.3)
                             inset=0.1,            # Відступи між панеллю та краєм її сектору
                             cell_rows=12, cell_cols=4):
    """
    genome: 2D numpy array {0,1}
    angles: 2D numpy array тих же розмірів (кут модуля, для підпису)
    """
    rows, cols = genome.shape

    # Фігура тепер враховує прямокутне співвідношення сторін секторів
    fig_w = max(6, cols * cell_width_ratio * 0.8)
    fig_h = max(6, rows * cell_height_ratio * 0.8)
    plt.figure(figsize=(fig_w, fig_h))
    
    ax = plt.gca()
    # Обмеження осей відповідають новим прямокутним секторам
    ax.set_xlim(0, cols * cell_width_ratio)
    ax.set_ylim(0, rows * cell_height_ratio)
    
    # Співвідношення сторін вікна відображення
    ax.set_aspect(cell_width_ratio / cell_height_ratio) 
    
    ax.set_facecolor("#eaeaea")
    plt.title("Solar Panel Layout (Rectangular Grid & Modules)")
    plt.xlabel(f"Columns (x {cell_width_ratio} units)")
    plt.ylabel(f"Rows (x {cell_height_ratio} units)")

    # Рисуємо сітку криші
    for c in range(cols + 1):
        ax.axvline(c * cell_width_ratio, color="white", linewidth=0.6)
    for r in range(rows + 1):
        ax.axhline(r * cell_height_ratio, color="white", linewidth=0.6)

    # Розміщення кожного модуля
    for r in range(rows):
        for c in range(cols):
            if genome[r, c] != 1:
                continue

            # Координати сектору (клітинки)
            cell_x_start = c * cell_width_ratio
            cell_y_start = (rows - r - 1) * cell_height_ratio # інвертуємо Y

            # Максимальні розміри модуля всередині сектору з відступами
            max_w = cell_width_ratio - 2 * inset
            max_h = cell_height_ratio - 2 * inset
            
            # Розрахунок розмірів модуля, який вписується у сектор зі збереженням panel_aspect
            # Модуль орієнтований вертикально: W = H / aspect
            mod_h = max_h
            mod_w = mod_h / panel_aspect
            
            # Якщо ширина модуля більша за дозволену
            if mod_w > max_w:
                mod_w = max_w
                mod_h = mod_w * panel_aspect

            # Координати для центрованого модуля в секторі
            x0 = cell_x_start + (cell_width_ratio / 2) - (mod_w / 2)
            y0 = cell_y_start + (cell_height_ratio / 2) - (mod_h / 2)

            _draw_module_icon(
                ax, x0, y0, mod_w, mod_h,
                cell_rows=cell_rows, cell_cols=cell_cols,
                angle_label=int(angles[r, c]) if angles is not None else None
            )

    os.makedirs("results/layouts", exist_ok=True)
    plt.tight_layout()
    out_path = os.path.join("results", "layouts", f"{filename}.png")
    plt.savefig(out_path, dpi=200)
    plt.close()