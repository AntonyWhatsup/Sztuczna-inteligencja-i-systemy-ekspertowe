import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ORANGE = "#ff8c00"  # рамка запрета монтажа 300 мм

def _draw_single_roof(ax, roof, panel, data, title=None):
    """
    Одна половина крыши со своей шкалой 0..W (мм).
    y=0 — гребень (рисуем тёмно-серым пунктиром).
    """
    # оси и гребень
    ax.set_xlim(0, roof.length)
    ax.set_ylim(0, roof.width)
    ax.axhline(0, color="dimgray", linestyle="--", linewidth=1.2)

    # внешний контур половины крыши
    ax.add_patch(Rectangle((0, 0), roof.length, roof.width,
                           linewidth=1.0, edgecolor="black", facecolor="none"))

    # рамка запрета установки (300 мм) — оранжевым
    bx = data.get("border_x", 300)
    by = data.get("border_y", 300)
    ax.add_patch(Rectangle((bx, by),
                           roof.length - 2*bx, roof.width - 2*by,
                           linewidth=1.2, edgecolor=ORANGE, facecolor="none"))

    # параметры укладки
    w, h = data["panel_w"], data["panel_h"]
    nx, ny = data["cols"], data["rows"]
    sx, sy = data.get("start_x", bx), data.get("start_y", by)
    gx, gy = getattr(panel, "gap_x", 0), getattr(panel, "gap_y", 0)
    cm = getattr(panel, "clamp_margin", 30)

    # панели — голубая заливка, синие края
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
    ax.set_xlabel("Длина (мм)")
    ax.set_ylabel("Расстояние от гребня (мм)")

def draw_two_roofs_columns(roof_left, roof_right, panel, data_left, data_right):
    """
    Две половины крыши в два ряда, у каждой шкала 0..W мм.
    Верхняя: 0 внизу (от гребня вверх). Нижняя: 0 вверху (от гребня вниз).
    Легенда: W, L, N, площадь панелей, площадь połaci — для каждой половины.
    """
    fig, (ax_top, ax_bot) = plt.subplots(nrows=2, ncols=1, figsize=(14, 8), sharex=False)
    fig.subplots_adjust(hspace=0.25)

    # верхняя половина
    _draw_single_roof(ax_top, roof_left, panel, data_left, title="Левая половина")
    # нижняя половина: инвертируем ось Y, чтобы 0 был наверху
    _draw_single_roof(ax_bot, roof_right, panel, data_right, title="Правая половина")
    ax_bot.invert_yaxis()

    # метрики для легенды
    def metrics(roof, data):
        N = data["total_panels"]
        w, h = data["panel_w"], data["panel_h"]
        A_panels_m2 = N * w * h / 1e6
        A_roof_m2 = roof.length * roof.width / 1e6
        return N, A_panels_m2, A_roof_m2

    N_L, APL, ARL = metrics(roof_left, data_left)
    N_R, APR, ARR = metrics(roof_right, data_right)

    legend = (
        f"Левая: W={roof_left.width} мм, L={roof_left.length} мм, N={N_L}, "
        f"Апанелей={APL:.2f} м², Аплощади={ARL:.2f} м² | "
        f"Правая: W={roof_right.width} мм, L={roof_right.length} мм, N={N_R}, "
        f"Апанелей={APR:.2f} м², Аплощади={ARR:.2f} м² "
        f"(border=300 мм, clamp=30 мм, gaps: gx={panel.gap_x} мм, gy={panel.gap_y} мм)"
    )
    fig.suptitle(legend, fontsize=9)

    plt.tight_layout()
    plt.show()

# алиас для совместимости со старым импортом
def draw_two_mirrored_roofs(roof_left, roof_right, panel, data_left, data_right, border=300):
    return draw_two_roofs_columns(roof_left, roof_right, panel, data_left, data_right)
