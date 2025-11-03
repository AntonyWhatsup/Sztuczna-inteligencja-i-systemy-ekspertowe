import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from typing import List, Tuple

ORANGE = "#ff8c00"  # border 300 mm + clearance przeszkód

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
        # strefa zakazu wokół przeszkody
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

# ОНОВЛЕНО: додано variant_note та параметри для приховування міток
def _draw_single_roof(ax, roof, panel, data, obstacles=None, title=None, variant_note=None, 
                     hide_xlabel=False, hide_ylabel=False):
    ax.set_xlim(0, roof.length)
    ax.set_ylim(0, roof.width)
    ax.axhline(0, color="dimgray", linestyle="--", linewidth=1.2)  # kalenica

    ax.add_patch(Rectangle((0, 0), roof.length, roof.width, linewidth=1.0, edgecolor="black", facecolor="none"))
    bx = data.get("border_x", 300); by = data.get("border_y", 300)
    ax.add_patch(Rectangle((bx, by), roof.length - 2*bx, roof.width - 2*by,
                           linewidth=1.4, edgecolor=ORANGE, facecolor="none"))

    if obstacles:
        _draw_obstacles(ax, obstacles)

    w, h = data["panel_w"], data["panel_h"]
    sx, sy = data.get("start_x", bx), data.get("start_y", by)
    gx, gy = getattr(panel, "gap_x", 0), getattr(panel, "gap_y", 0)
    cm = getattr(panel, "clamp_margin", 30)

    rects = data.get("placed_rects") or []
    for (px, py, pw, ph) in rects:
        ax.add_patch(Rectangle((px, py), pw, ph, linewidth=1.0, edgecolor="tab:blue",
                               facecolor="skyblue", alpha=0.35))
        if pw > 2*cm and ph > 2*cm:
            ax.add_patch(Rectangle((px+cm, py+cm), pw-2*cm, ph-2*cm,
                                   linewidth=0.8, edgecolor="gray", facecolor="none", linestyle="--"))

    ax.grid(True, linestyle=":", linewidth=0.5)
    
    # Регулювання заголовку
    full_title = title
    if variant_note:
        full_title = f"{variant_note} | {title}" # Компактніше розташування
        
    if full_title: ax.set_title(full_title, fontsize=8) # Зменшуємо розмір шрифту заголовка
    
    # Приховуємо мітки на внутрішніх графіках
    if not hide_xlabel:
        ax.set_xlabel("Długość (mm)", fontsize=8)
    else:
        ax.set_xlabel("")
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        
    if not hide_ylabel: 
        ax.set_ylabel("Odległość od kalenicy (mm)", fontsize=8)
    else:
        ax.set_ylabel("")
        ax.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)


def draw_comparison_grid(roof_left, roof_right, panel, obstacles_left, obstacles_right, 
                           best_variants: List[Tuple[int, str, str, dict, dict]], 
                           save_path: str = None, show: bool = True):
    
    variants_to_plot = best_variants[:3]
    num_variants = len(variants_to_plot)
    
    if num_variants == 0:
        print("No variants to plot.")
        return

    # ЗМЕНШЕННЯ ВИСОТИ ТА ЗБІЛЬШЕННЯ ПРОСТОРУ:
    # 1. Зменшено базову висоту з 4.5 до 3.5
    # 2. Збільшено hspace
    fig, axes = plt.subplots(nrows=num_variants, ncols=2, figsize=(14, 3.5 * num_variants), sharex=False)
    fig.subplots_adjust(hspace=0.5, wspace=0.3) 
    
    if num_variants == 1:
        axes = axes.reshape(1, -1)

    all_metrics = []
    
    for i, (N_total, align_x, align_y, data_L, data_R) in enumerate(variants_to_plot):
        
        def metrics(roof, data):
            N = data["total_panels"]; w, h = data["panel_w"], data["panel_h"]
            return N, (N*w*h)/1e6 # N, Apaneli (m²)
        
        N_L, APL = metrics(roof_left, data_L)
        N_R, APR = metrics(roof_right, data_R)
        
        all_metrics.append({
            "rank": i + 1,
            "N_total": N_total,
            "N_L": N_L,
            "N_R": N_R,
            "align": f"{align_x}/{align_y}"
        })

        # Примітка для варіанту (з'явиться у заголовку лівого схилу)
        variant_note = f"Rank {i+1}: Total N={N_total}"
        
        # Визначаємо, які мітки приховувати
        hide_x = (i < num_variants - 1)
        hide_y_left = True
        hide_y_right = True
        
        # Малюємо Лівий Схил
        ax_left = axes[i, 0]
        _draw_single_roof(ax_left, roof_left, panel, data_L, 
                          obstacles=obstacles_left, 
                          title=f"Lewa ({align_x}/{align_y}) | N:{N_L}, A:{APL:.2f} m²", 
                          variant_note=variant_note if i==0 else None, # Залишаємо повну примітку тільки для Rank 1
                          hide_xlabel=hide_x, hide_ylabel=hide_y_left)
        
        # Малюємо Правий Схил
        ax_right = axes[i, 1]
        _draw_single_roof(ax_right, roof_right, panel, data_R, 
                          obstacles=obstacles_right, 
                          title=f"Prawa ({align_x}/{align_y}) | N:{N_R}, A:{APR:.2f} m²", 
                          variant_note=None,
                          hide_xlabel=hide_x, hide_ylabel=hide_y_right)

        # Інвертуємо Y-вісь для правого схилу
        ax_right.invert_yaxis()

    # Формуємо загальний супер-заголовок
    overall_legend = "--- Comparison of Top Layouts (N - Total Panels) ---\n"
    for m in all_metrics:
        overall_legend += f"Rank {m['rank']} (Align: {m['align']}): N_Total={m['N_total']} (N_L:{m['N_L']}, N_R:{m['N_R']})\n"
        
    overall_legend += (f"\nConfiguration: Border=300 mm; Gaps: gx={panel.gap_x} mm, gy={panel.gap_y} mm; Clamp={panel.clamp_margin} mm.")
    
    fig.suptitle(overall_legend, fontsize=10, y=1.0) 

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # Зберігаємо графік з компактним макетом
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
        
    if show:
        # Регулюємо макет для супер-заголовка
        plt.tight_layout(rect=[0, 0, 1, 0.95]) # Підняли rect[3] з 0.9 до 0.95
        plt.show()
    else:
        plt.close(fig)
        
    return fig

# СТАРУ функцію draw_two_roofs_columns видалено.