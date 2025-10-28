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

# alias dla kompatybilności ze starym importem (аліас для сумісності зі старим імпортом)
def draw_two_mirrored_roofs(roof_left, roof_right, panel, data_left, data_right, border=300):
    return draw_two_roofs_columns(roof_left, roof_right, panel, data_left, data_right)