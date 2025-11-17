# visualization.py
import os
import sys
from config import Config
from roof import Roof
from panel import Panel, best_orientation, fill_roof_with_panels, fill_with_obstacles, augment_with_gap_portraits

# Import our new, modularized plot functions
from plotter_top_view import draw_two_roofs_columns
from project_utils import Obstacle, assert_layout_valid, export_csv, _overlap  # _overlap added for logging

# ---------- CALCULATION AND COMPARISON FUNCTION ----------
def calculate_best_layout(roof, panel_base, BORDER, obstacles, orientation_hint):
    """
    Performs a full calculation for a given orientation,
    including masking obstacles and additional gap filling.
    """
    if orientation_hint == "auto":
        # This chooses the best base grid P or L without obstacles
        choice = best_orientation(L=roof.length, W=roof.width, m_x=BORDER, m_y=BORDER,
                                  gx=panel_base.gap_x, gy=panel_base.gap_y,
                                  w_portrait=panel_base.width, h_portrait=panel_base.height)
        orientation_hint = choice["orientation"]

    # 1. Base grid
    base_data = fill_roof_with_panels(roof, panel_base, BORDER, BORDER, orientation=orientation_hint)
    
    # 2. Mask obstacles
    data_masked = fill_with_obstacles(roof, panel_base, base_data, obstacles)
    
    # 3. Additional augmentation
    final_data = augment_with_gap_portraits(roof, panel_base, data_masked, obstacles)
    
    return final_data

# ---------- MAIN TOP VIEW CALCULATION ----------
def run_top_view_calculation():
    print("--- [START] Running 'Top View' calculation ---")
    cfg = Config()  

    # 1. Initialize models
    roof_left  = Roof(width=cfg.roof_left.width,  length=cfg.roof_left.length)
    roof_right = Roof(width=cfg.roof_right.width, length=cfg.roof_right.length)
    BORDER = cfg.roof_left.border 

    panel_base = Panel(width=cfg.panel.width, height=cfg.panel.height,
                       gap_x=cfg.panel.gap_x, gap_y=cfg.panel.gap_y, clamp_margin=cfg.panel.clamp)

    obstacles_left = [Obstacle(**vars(o)) for o in cfg.obstacles_left]
    obstacles_right = [Obstacle(**vars(o)) for o in cfg.obstacles_right]

    # 2. Generate and compare layouts for LEFT roof
    
    # Attempt 1: Portrait orientation as base
    data_L_P = calculate_best_layout(roof_left, panel_base, BORDER, obstacles_left, "portrait")
    # Attempt 2: Landscape orientation as base
    data_L_L = calculate_best_layout(roof_left, panel_base, BORDER, obstacles_left, "landscape")
    
    data_L = data_L_P if data_L_P["total_panels"] >= data_L_L["total_panels"] else data_L_L
    print(f"[LEFT ROOF] Best Layout: {data_L['total_panels']} panels. (P={data_L_P['total_panels']}, L={data_L_L['total_panels']})")

    # 3. Generate and compare layouts for RIGHT roof

    data_R_P = calculate_best_layout(roof_right, panel_base, BORDER, obstacles_right, "portrait")
    data_R_L = calculate_best_layout(roof_right, panel_base, BORDER, obstacles_right, "landscape")
    
    data_R = data_R_P if data_R_P["total_panels"] >= data_R_L["total_panels"] else data_R_L
    print(f"[RIGHT ROOF] Best Layout: {data_R['total_panels']} panels. (P={data_R_P['total_panels']}, L={data_R_L['total_panels']})")
    
    print(f"[TOTAL] Panels placed: {data_L['total_panels'] + data_R['total_panels']}")

    # 4. Validation
    try:
        assert_layout_valid(roof_left,  BORDER, data_L, obstacles_left)
        assert_layout_valid(roof_right, BORDER, data_R, obstacles_right)
        print("[CHECK] Collision tests: OK")
    except AssertionError as e:
        print(f"!!! [ERROR] VALIDATION FAILED: {e}")
        # Stop if validation fails
        return

    # 5. Visualization and export
    png_path = os.path.join(cfg.out_dir, "top_view.png") if cfg.save_png else None
    
    # Use panel parameters from the selected best result
    panel_for_plot = Panel(width=data_L["panel_w"], height=data_L["panel_h"],
                           gap_x=panel_base.gap_x, gap_y=panel_base.gap_y, clamp_margin=panel_base.clamp_margin)
    
    draw_two_roofs_columns(roof_left, roof_right, panel_for_plot, data_L, data_R,
                           obstacles_left=obstacles_left, obstacles_right=obstacles_right,
                           save_path=png_path, show=True)
    if png_path:
        print(f"[SAVE] PNG saved at: {os.path.abspath(png_path)}")

    if cfg.save_csv:
        csv_L_path = os.path.join(cfg.out_dir, "panels_left.csv")
        csv_R_path = os.path.join(cfg.out_dir, "panels_right.csv")
        export_csv(csv_L_path, "L", data_L, panel_base)
        export_csv(csv_R_path, "R", data_R, panel_base)
        print(f"[SAVE] CSV saved at: {os.path.abspath(cfg.out_dir)}")
    
    print("--- [END] 'Top View' calculation finished ---")


if __name__ == "__main__":
    run_top_view_calculation()
