# visualization.py
import os
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

# ---------- 1) PARETO FRONT (стоимость ↔ энергия) ----------
def plot_pareto_front(results, filename="pareto_front.png"):
    """
    results: list of tuples (genome, (energy, cost, shadow))
    """
    energies = [r[1][0] for r in results]
    costs    = [r[1][1] for r in results]
    shadows  = [r[1][2] for r in results]

    plt.figure()
    plt.scatter(costs, energies, c=shadows)  # цвет = %тени
    plt.xlabel("Cost (PLN)")
    plt.ylabel("Annual Energy (kWh)")
    cbar = plt.colorbar()
    cbar.set_label("Shadow (%)")
    plt.title("Pareto Front: Cost vs Energy")

    os.makedirs("results", exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join("results", filename), dpi=150)
    plt.close()

# ---------- 2) PARETO CHART (столбцы + кумулятив) ----------
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

# ---------- 3) ИКОНКА МОДУЛЯ КАК НА РЕФЕРЕНСЕ ----------
def _draw_module_icon(
    ax, x, y, w, h,
    cell_rows=12, cell_cols=4,
    draw_hole=True,
    angle_label=None
):
    """
    Рисует тонкий вертикальный модуль с белой рамкой и чёрной решёткой ячеек.
    Без проводов. Ориентируется по прямоугольнику (x,y,w,h).
    """
    # Внешняя белая рамка со скруглением
    rr = min(w, h) * 0.12  # радиус скругления
    frame = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0.02,rounding_size={rr}",
                           linewidth=1.5, edgecolor="black", facecolor="white")
    ax.add_patch(frame)

    # Внутреннее "стекло" — оставляем белым, клетки нарисуем поверх
    margin = 0.06 * min(w, h)
    gx, gy = x + margin, y + margin
    gw, gh = w - 2 * margin, h - 2 * margin

    # Отверстие сверху по центру (как на фото)
    if draw_hole:
        r = min(w, h) * 0.03
        ax.add_patch(Circle((x + w/2, y + h - margin*0.55), r, facecolor="white", edgecolor="lightgray"))

    # Сетка ячеек: чёрные прямоугольники с белыми "швами"
    gap = 0.08  # доля шага под зазор
    dx, dy = gw / cell_cols, gh / cell_rows
    pad_x, pad_y = dx * gap, dy * gap
    for r_i in range(cell_rows):
        for c_i in range(cell_cols):
            cx = gx + c_i * dx + pad_x/2
            cy = gy + r_i * dy + pad_y/2
            ax.add_patch(Rectangle((cx, cy), dx - pad_x, dy - pad_y,
                                   facecolor="black", edgecolor="black", linewidth=0.2))

    # Необязательная подпись угла
    if angle_label is not None:
        ax.text(x + w/2, y + margin*0.5, f"{angle_label}°", ha="center", va="bottom", fontsize=7)

# ---------- 4) ПЛАН КРЫШИ С МОДУЛЯМИ-ИКОНКАМИ ----------
def visualize_grid_layout(genome, angles, filename,
                          panel_aspect=2.3,  # высота/ширина как у тонкого модуля
                          cell_rows=12, cell_cols=4):
    """
    genome: 2D numpy array {0,1}
    angles: 2D numpy array тех же размеров (угол модуля, для подписи)
    На каждую ячейку с 1 рисуется модуль в стиле референса.
    """
    rows, cols = genome.shape

    fig_w = max(6, cols * 0.9)
    fig_h = max(6, rows * 0.9)
    plt.figure(figsize=(fig_w, fig_h))
    ax = plt.gca()
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.set_facecolor("#eaeaea")
    plt.title("Solar Panel Layout (Reference-style Modules)")
    plt.xlabel("Columns")
    plt.ylabel("Rows")

    # Рисуем сетку крыши
    for c in range(cols + 1):
        ax.axvline(c, color="white", linewidth=0.6)
    for r in range(rows + 1):
        ax.axhline(r, color="white", linewidth=0.6)

    # Каждый модуль вписываем в ячейку 1×1 с нужным аспектом
    inset = 0.08  # поля внутри клетки
    for r in range(rows):
        for c in range(cols):
            if genome[r, c] != 1:
                continue

            # Координаты клетки (нижний левый угол в системе matplotlib)
            cell_x = c
            cell_y = rows - r - 1  # инвертируем Y, чтобы (0,0) был внизу слева

            # Рассчитываем размеры модуля с сохранением panel_aspect
            max_w = 1 - 2 * inset
            max_h = 1 - 2 * inset
            mod_h = min(max_h, max_w * panel_aspect)
            mod_w = mod_h / panel_aspect
            if mod_w > max_w:  # редкий случай — подгон по ширине
                mod_w = max_w
                mod_h = mod_w * panel_aspect

            x0 = cell_x + 0.5 - mod_w / 2
            y0 = cell_y + 0.5 - mod_h / 2

            _draw_module_icon(
                ax, x0, y0, mod_w, mod_h,
                cell_rows=cell_rows, cell_cols=cell_cols,
                draw_hole=True,
                angle_label=int(angles[r, c]) if angles is not None else None
            )

    os.makedirs("results/layouts", exist_ok=True)
    plt.tight_layout()
    out_path = os.path.join("results", "layouts", f"{filename}.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    
# --- Backward-compat shim ---
def plot_pareto(results):
    # сохраняет прежнее имя для evolution.py
    return plot_pareto_front(results, filename="pareto.png")
