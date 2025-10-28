import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ORANGE = "#ff8c00"  # ramka zakazu montażu 300 mm (рамка заборони монтажу 300 мм)

def _draw_single_roof(ax, roof, panel, data, title=None):
    """
    Jedna połać dachu ze skalą 0..W (mm).
    y=0 — kalenica (rysujemy ciemnoszarą przerywaną linią).
    """
    # osie i kalenica (осі та гребінь)
    ax.set_xlim(0, roof.length)
    ax.set_ylim(0, roof.width)
    ax.axhline(0, color="dimgray", linestyle="--", linewidth=1.2)

    # zewnętrzny kontur połaci dachu (зовнішній контур половини даху)
    ax.add_patch(Rectangle((0, 0), roof.length, roof.width,
                           linewidth=1.0, edgecolor="black", facecolor="none"))

    # ramka zakazu instalacji (300 mm) — pomarańczowa (рамка заборони установки (300 мм) — помаранчевим)
    bx = data.get("border_x", 300)
    by = data.get("border_y", 300)
    ax.add_patch(Rectangle((bx, by),
                           roof.length - 2*bx, roof.width - 2*by,
                           linewidth=1.2, edgecolor=ORANGE, facecolor="none"))

    # parametry układu (параметри укладання)
    w, h = data["panel_w"], data["panel_h"]
    nx, ny = data["cols"], data["rows"]
    sx, sy = data.get("start_x", bx), data.get("start_y", by)
    gx, gy = getattr(panel, "gap_x", 0), getattr(panel, "gap_y", 0)
    cm = getattr(panel, "clamp_margin", 30)

    # panele — jasnoniebieskie wypełnienie, niebieskie krawędzie (панелі — блакитна заливка, сині краї)
    for r in range(ny):
        y = sy + r * (h + gy)
        for c in range(nx):
            x = sx + c * (w + gx)
            ax.add_patch(Rectangle((x, y), w, h,
                                   linewidth=1.0, edgecolor="tab:blue",
                                   facecolor="skyblue", alpha=0.35))
            if w > 2*cm and h > 2*cm:
                ax.add_patch(Rectangle((x + cm, y + cm),
                                       w - 2*cm, h - 2*cm,
                                       linewidth=0.8, edgecolor="gray",
                                       facecolor="none", linestyle="--"))

    ax.grid(True, linestyle=":", linewidth=0.5)
    if title:
        ax.set_title(title, fontsize=10)
    ax.set_xlabel("Długość (mm)") # Довжина (мм)
    ax.set_ylabel("Odległość od kalenicy (mm)") # Відстань від гребеня (мм)

def draw_two_roofs_columns(roof_left, roof_right, panel, data_left, data_right):
    """
    Dwie połacie dachu w dwóch rzędach, każda ze skalą 0..W mm.
    Górna: 0 na dole (od kalenicy w górę). Dolna: 0 na górze (od kalenicy w dół).
    Legenda: W, L, N, powierzchnia paneli, powierzchnia połaci — dla każdej połaci.
    """
    fig, (ax_top, ax_bot) = plt.subplots(nrows=2, ncols=1, figsize=(14, 8), sharex=False)
    fig.subplots_adjust(hspace=0.25)

    # górna połać (верхня половина)
    _draw_single_roof(ax_top, roof_left, panel, data_left, title="Lewa Połać") # Ліва половина
    # dolna połać: odwracamy oś Y, aby 0 był na górze (нижня половина: інвертуємо вісь Y, щоб 0 був нагорі)
    _draw_single_roof(ax_bot, roof_right, panel, data_right, title="Prawa Połać") # Права половина
    ax_bot.invert_yaxis()

    # metryki dla legendy (метрики для легенди)
    def metrics(roof, data):
        N = data["total_panels"]
        w, h = data["panel_w"], data["panel_h"]
        A_panels_m2 = N * w * h / 1e6
        A_roof_m2 = roof.length * roof.width / 1e6
        return N, A_panels_m2, A_roof_m2

    N_L, APL, ARL = metrics(roof_left, data_left)
    N_R, APR, ARR = metrics(roof_right, data_right)

    legend = (
        f"Lewa: W={roof_left.width} mm, L={roof_left.length} mm, N={N_L}, "
        f"Apaneli={APL:.2f} m², Adachu={ARL:.2f} m² | "
        f"Prawa: W={roof_right.width} mm, L={roof_right.length} mm, N={N_R}, "
        f"Apaneli={APR:.2f} m², Adachu={ARR:.2f} m² "
        f"(margines=300 mm, zacisk=30 mm, odstępy: gx={panel.gap_x} mm, gy={panel.gap_y} mm)"
    )
    fig.suptitle(legend, fontsize=9)

    plt.tight_layout()
    plt.show()

<<<<<<< Updated upstream
# alias dla kompatybilności ze starym importem (аліас для сумісності зі старим імпортом)
def draw_two_mirrored_roofs(roof_left, roof_right, panel, data_left, data_right, border=300):
    return draw_two_roofs_columns(roof_left, roof_right, panel, data_left, data_right)
=======
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
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

def _draw_module_icon(ax, x, y, w, h, cell_rows=12, cell_cols=4, draw_hole=True, angle_label=None):
    """Вертикальный тонкий модуль: белая рамка + решётка чёрных ячеек, без проводов."""
    rr = min(w, h) * 0.12
    frame = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0.02,rounding_size={rr}",
                           linewidth=1.5, edgecolor="black", facecolor="white")
    ax.add_patch(frame)

    margin = 0.06 * min(w, h)
    gx, gy = x + margin, y + margin
    gw, gh = w - 2 * margin, h - 2 * margin

    if draw_hole:
        r = min(w, h) * 0.03
        ax.add_patch(Circle((x + w/2, y + h - margin*0.55), r, facecolor="white", edgecolor="lightgray"))

    gap = 0.08
    dx, dy = gw / cell_cols, gh / cell_rows
    pad_x, pad_y = dx * gap, dy * gap
    for r_i in range(cell_rows):
        for c_i in range(cell_cols):
            cx = gx + c_i * dx + pad_x/2
            cy = gy + r_i * dy + pad_y/2
            ax.add_patch(Rectangle((cx, cy), dx - pad_x, dy - pad_y,
                                   facecolor="black", edgecolor="black", linewidth=0.2))

    if angle_label is not None:
        ax.text(x + w/2, y + margin*0.5, f"{int(angle_label)}°",
                ha="center", va="bottom", fontsize=7, color="#4FC3F7")  # светло-синий

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
>>>>>>> Stashed changes
