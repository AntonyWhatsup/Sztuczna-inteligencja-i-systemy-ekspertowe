import os, csv
from panel import (
    Panel, best_orientation, fill_roof_with_panels,
    fill_with_obstacles, augment_with_gap_portraits
)

from dataclasses import dataclass
from typing import List, Tuple

from config import Config
from roof import Roof
# IMPORT UPDATED: now importing the grid comparison renderer
from visualization import draw_comparison_grid 


# Local Obstacle class for rendering + inflated() expansion
@dataclass
class Obstacle:
    side: str
    x: float; y: float; w: float; h: float
    clearance: float = 0.0
    elev: float = 0.0
    type: str = "generic"
    frame_t: float = 80.0
    grid_cols: int = 2
    grid_rows: int = 3
    cap_over: float = 80.0
    def inflated(self):
        c = self.clearance
        return (self.x - c, self.y - c, self.w + 2*c, self.h + 2*c)


# ---------- layout validator ----------
def _overlap(ax, ay, aw, ah, bx, by, bw, bh) -> bool:
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)

def assert_layout_valid(roof, border, data, obstacles: List[Obstacle]) -> None:
    L, W = roof.length, roof.width
    bx, by = border, border
    rects = data.get("placed_rects", [])
    # border check
    for (x, y, w, h) in rects:
        if not (x >= bx and y >= by and x + w <= L - bx and y + h <= W - by):
            raise AssertionError(f"Panel out of border: {(x,y,w,h)}")
        if w <= 0 or h <= 0:
            raise AssertionError(f"Degenerate panel: {(x,y,w,h)}")
    # obstacle collisions
    masks = [ob.inflated() for ob in obstacles]
    for (x, y, w, h) in rects:
        for (mx, my, mw, mh) in masks:
            if _overlap(x, y, w, h, mx, my, mw, mh):
                raise AssertionError(f"Collision with obstacle at {(mx,my,mw,mh)} by {(x,y,w,h)}")


# ---------- CSV export ----------
def export_csv(path: str, side: str, data, panel: Panel):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rects = data.get("placed_rects", [])
    sx, sy = data["start_x"], data["start_y"]
    w, h = data["panel_w"], data["panel_h"]
    gx, gy = panel.gap_x, panel.gap_y
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["side", "x_mm", "y_mm", "w_mm", "h_mm", "row", "col"])
        for (x, y, pw, ph) in rects:
            r = round((y - sy) / (h + gy)) if (h + gy) > 0 else 0
            c = round((x - sx) / (w + gx)) if (w + gx) > 0 else 0
            wr.writerow([side, int(round(x)), int(round(y)), int(round(pw)), int(round(ph)), r, c])


# ---------- main execution ----------
if __name__ == "__main__":
    cfg = Config()  # stage 2 configuration

    # roof geometry
    roof_left  = Roof(width=cfg.roof_left.width,  length=cfg.roof_left.length)
    roof_right = Roof(width=cfg.roof_right.width, length=cfg.roof_right.length)
    BORDER = cfg.roof_left.border  # same for both sides

    # base panel
    panel_base = Panel(
        width=cfg.panel.width, height=cfg.panel.height,
        gap_x=cfg.panel.gap_x, gap_y=cfg.panel.gap_y,
        clamp_margin=cfg.panel.clamp
    )

    # obstacles from config
    obstacles_left = [Obstacle(**vars(o)) for o in cfg.obstacles_left]
    obstacles_right = [Obstacle(**vars(o)) for o in cfg.obstacles_right]

    # --- UPDATED "GENERATION-BASED" APPROACH ---
    
    # 1. Determine the best ORIENTATION first (portrait or landscape)
    choice = best_orientation(
        L=roof_left.length, W=roof_left.width,
        m_x=BORDER, m_y=BORDER,
        gx=panel_base.gap_x, gy=panel_base.gap_y,
        w_portrait=panel_base.width, h_portrait=panel_base.height
    )
    orientation = choice["orientation"]
    print(f"[CONFIG] Base orientation={orientation}, N_base={choice['N']}")

    # 2. Evaluate all 9 alignment options and store top-3
    print("[Optimizing] Trying 9 layout alignment 'generations'...")
    align_x_opts = ["left", "center", "right"]
    align_y_opts = ["top", "center", "bottom"]  # 'top' = near ridge

    # Store (N_total, align_x, align_y, data_L, data_R)
    best_variants: List[Tuple[int, str, str, dict, dict]] = []
    
    for align_x in align_x_opts:
        for align_y in align_y_opts:
            # A. Build base grid
            base_L = fill_roof_with_panels(
                roof_left, panel_base, BORDER, BORDER,
                orientation=orientation, align_x=align_x, align_y=align_y
            )
            base_R = fill_roof_with_panels(
                roof_right, panel_base, BORDER, BORDER,
                orientation=orientation, align_x=align_x, align_y=align_y
            )
                                           
            # B. Remove panels colliding with obstacles
            data_L_variant = fill_with_obstacles(
                roof_left, panel_base, base_L, obstacles_left
            )
            data_R_variant = fill_with_obstacles(
                roof_right, panel_base, base_R, obstacles_right
            )
            
            # C. Fill gaps with portrait panels
            data_L_variant = augment_with_gap_portraits(
                roof_left, panel_base, data_L_variant, obstacles_left
            )
            data_R_variant = augment_with_gap_portraits(
                roof_right, panel_base, data_R_variant, obstacles_right
            )
            
            # D. Count results
            N_total = (
                data_L_variant["total_panels"]
                + data_R_variant["total_panels"]
            )
            print(f"  [Variant] align=({align_x}, {align_y}), N_Total={N_total}")
            
            result = (N_total, align_x, align_y, data_L_variant, data_R_variant)
            best_variants.append(result)
            
            # Keep only top-3
            best_variants.sort(key=lambda x: x[0], reverse=True)
            best_variants = best_variants[:3]
            

    # Select the best layout out of the 9 "generations"
    data_L, data_R = best_variants[0][3], best_variants[0][4]
    best_N = best_variants[0][0]
    print(f"[Optimizing] Best layout found with N_Total={best_N} panels.")
    # --- END OF NEW APPROACH ---

    # validation
    assert_layout_valid(roof_left,  BORDER, data_L, obstacles_left)
    assert_layout_valid(roof_right, BORDER, data_R, obstacles_right)
    print("[CHECK] collision tests: OK")

    # visualization → PNG
    png_path = (
        os.path.join(cfg.out_dir, "top_view_comparison.png")
        if cfg.save_png else None
    )
    
    panel_for_plot = Panel(
        width=data_L["panel_w"], height=data_L["panel_h"],
        gap_x=panel_base.gap_x, gap_y=panel_base.gap_y,
        clamp_margin=panel_base.clamp_margin
    )
    
    # NEW CALL: plot the top-3 variants on one comparison grid
    draw_comparison_grid(
        roof_left, roof_right, panel_for_plot,
        obstacles_left, obstacles_right,
        best_variants,
        save_path=png_path, show=True
    )

    # CSV export (only best variant)
    if cfg.save_csv:
        export_csv(
            os.path.join(cfg.out_dir, "panels_left.csv"),
            "L", data_L, panel_for_plot
        )
        export_csv(
            os.path.join(cfg.out_dir, "panels_right.csv"),
            "R", data_R, panel_for_plot
        )
        print("[EXPORT] CSV saved in", cfg.out_dir)
