# plotter_top_view.py
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ORANGE = "#ff8c00"  # 300 mm border + obstacle clearance

def _inflate_rect(ob):
    if isinstance(ob, dict):
        x, y, w, h = ob["x"], ob["y"], ob["w"], ob["h"]
        c = ob.get("clearance", 0.0)
        typ = ob.get("type", "generic")
        params = ob
    else:
        x, y, w, h = ob.x, ob.y, ob.w, ob.h
        c = getattr(ob, "clearance", 0.0)
        typ = getattr(ob, "type", "generic")
        params = ob
    return (x, y, w, h), (x - c, y - c, w + 2*c, h + 2*c), typ, params

def _draw_obstacles(ax, obstacles):
    for ob in obstacles:
        (x, y, w, h), (xi, yi, wi, hi), typ, p = _inflate_rect(ob)
        # forbidden zone around the obstacle
        ax.add_patch(Rectangle((xi, yi), wi, hi,
                               linewidth=1.2, edgecolor=ORANGE,
                               facecolor=ORANGE, alpha=0.12, hatch="////"))
        if typ == "window":
            ft = float(getattr(p, "frame_t", 80.0))
            gc = max(1, int(getattr(p, "grid_cols", 2)))
            gr = max(1, int(getattr(p, "grid_rows", 3)))
            ax.add_patch(Rectangle((x, y), w, h, linewidth=2.0, edgecolor="navy", facecolor="none"))
            ax.add_patch(Rectangle((x+ft, y+ft), w-2*ft, h-2*ft, linewidth=1.0, edgecolor="navy", facecolor="none"))
            for i in range(1, gc):
                xx = x + ft + i*(w-2*ft)/gc
                ax.plot([xx, xx], [y+ft, y+h-ft], color="navy", linewidth=1.0)
            for j in range(1, gr):
                yy = y + ft + j*(h-2*ft)/gr
                ax.plot([x+ft, x+w-ft], [yy, yy], color="navy", linewidth=1.0)
        elif typ == "chimney":
            ax.add_patch(Rectangle((x, y), w, h, linewidth=1.2, edgecolor="crimson", facecolor="none"))
            over = float(getattr(p, "cap_over", 80.0))
            ax.add_patch(Rectangle((x - over, y - over), w + 2*over, h + 2*over,
                                   linewidth=1.2, edgecolor="crimson", facecolor="none"))
        else:
            ax.add_patch(Rectangle((x, y), w, h, linewidth=1.0, edgecolor="crimson", facecolor="none"))

def _draw_single_roof(ax, roof, panel, data, obstacles=None, title=None):
    ax.set_xlim(0, roof.length)
    ax.set_ylim(0, roof.width)
    ax.axhline(0, color="dimgray", linestyle="--", linewidth=1.2)  # ridge

    ax.add_patch(Rectangle((0, 0), roof.length, roof.width, linewidth=1.0, edgecolor="black", facecolor="none"))
    bx = data.get("border_x", 300); by = data.get("border_y", 300)
    ax.add_patch(Rectangle((bx, by), roof.length - 2*bx, roof.width - 2*by,
                           linewidth=1.4, edgecolor=ORANGE, facecolor="none"))

    if obstacles:
        _draw_obstacles(ax, obstacles)

    w, h = data["panel_w"], data["panel_h"]
    nx, ny = data["cols"], data["rows"]
    sx, sy = data.get("start_x", bx), data.get("start_y", by)
    gx, gy = getattr(panel, "gap_x", 0), getattr(panel, "gap_y", 0)
    cm = getattr(panel, "clamp_margin", 30)

    rects = data.get("placed_rects") or [(sx + c*(w+gx), sy + r*(h+gy), w, h) for r in range(ny) for c in range(nx)]
    for (px, py, pw, ph) in rects:
        ax.add_patch(Rectangle((px, py), pw, ph, linewidth=1.0, edgecolor="tab:blue",
                               facecolor="skyblue", alpha=0.35))
        if pw > 2*cm and ph > 2*cm:
            ax.add_patch(Rectangle((px+cm, py+cm), pw-2*cm, ph-2*cm,
                                   linewidth=0.8, edgecolor="gray", facecolor="none", linestyle="--"))

    ax.grid(True, linestyle=":", linewidth=0.5)
    if title: ax.set_title(title, fontsize=10)
    ax.set_xlabel("Length (mm)"); ax.set_ylabel("Distance from ridge (mm)")

def draw_two_roofs_columns(roof_left, roof_right, panel, data_left, data_right,
                           obstacles_left=None, obstacles_right=None,
                           save_path: str = None, show: bool = True):
    fig, (ax_top, ax_bot) = plt.subplots(nrows=2, ncols=1, figsize=(14, 8), sharex=False)
    fig.subplots_adjust(hspace=0.25)

    _draw_single_roof(ax_top, roof_left,  panel, data_left,  obstacles=obstacles_left,  title="Left Roof")
    _draw_single_roof(ax_bot, roof_right, panel, data_right, obstacles=obstacles_right, title="Right Roof")
    ax_bot.invert_yaxis()

    def metrics(roof, data):
        N = data["total_panels"]; w, h = data["panel_w"], data["panel_h"]
        return N, (N*w*h)/1e6, (roof.length*roof.width)/1e6

    N_L, APL, ARL = metrics(roof_left, data_left)
    N_R, APR, ARR = metrics(roof_right, data_right)

    legend = (f"Left: W={roof_left.width} mm, L={roof_left.length} mm, N={N_L}, "
              f"PanelsArea={APL:.2f} m², RoofArea={ARL:.2f} m² | "
              f"Right: W={roof_right.width} mm, L={roof_right.length} mm, N={N_R}, "
              f"PanelsArea={APR:.2f} m², RoofArea={ARR:.2f} m² "
              f"(border=300 mm; forbidden zones=orange; clamp=30 mm; "
              f"gaps: gx={panel.gap_x} mm, gy={panel.gap_y} mm)")
    fig.suptitle(legend, fontsize=9)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
    if show:
        plt.tight_layout(); plt.show()
    else:
        plt.close(fig)
    return fig
