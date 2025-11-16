# visualization.py
import os
import sys
from config import Config
from roof import Roof
from panel import Panel, best_orientation, fill_roof_with_panels, fill_with_obstacles, augment_with_gap_portraits

# Імпортуємо наші нові, розділені модулі
from plotter_top_view import draw_two_roofs_columns
from project_utils import Obstacle, assert_layout_valid, export_csv, _overlap # _overlap додано для log

# ---------- ФУНКЦІЯ РОЗРАХУНКУ І ПОРІВНЯННЯ ----------
def calculate_best_layout(roof, panel_base, BORDER, obstacles, orientation_hint):
    """
    Виконує повний розрахунок для заданої орієнтації, 
    включаючи маскування перешкод та додаткове заповнення проміжків.
    """
    if orientation_hint == "auto":
        # Це вибере найкращу базову сітку P або L без перешкод
        choice = best_orientation(L=roof.length, W=roof.width, m_x=BORDER, m_y=BORDER,
                                  gx=panel_base.gap_x, gy=panel_base.gap_y,
                                  w_portrait=panel_base.width, h_portrait=panel_base.height)
        orientation_hint = choice["orientation"]

    # 1. Базова сітка (Grid)
    base_data = fill_roof_with_panels(roof, panel_base, BORDER, BORDER, orientation=orientation_hint)
    
    # 2. Маскування перешкод (Obstacles)
    data_masked = fill_with_obstacles(roof, panel_base, base_data, obstacles)
    
    # 3. Додаткове заповнення (Augmentation)
    final_data = augment_with_gap_portraits(roof, panel_base, data_masked, obstacles)
    
    return final_data

# ---------- ОСНОВНИЙ ЗАПУСК РОЗРАХУНКУ ----------
def run_top_view_calculation():
    print("--- [START] Запуск розрахунку 'Top View' ---")
    cfg = Config()  

    # 1. Ініціалізація моделей
    roof_left  = Roof(width=cfg.roof_left.width,  length=cfg.roof_left.length)
    roof_right = Roof(width=cfg.roof_right.width, length=cfg.roof_right.length)
    BORDER = cfg.roof_left.border 

    panel_base = Panel(width=cfg.panel.width, height=cfg.panel.height,
                       gap_x=cfg.panel.gap_x, gap_y=cfg.panel.gap_y, clamp_margin=cfg.panel.clamp)

    obstacles_left = [Obstacle(**vars(o)) for o in cfg.obstacles_left]
    obstacles_right = [Obstacle(**vars(o)) for o in cfg.obstacles_right]

    # 2. Генерація та порівняння розкладок для ЛІВОГО даху
    
    # Спроба 1: Портретна орієнтація як базова
    data_L_P = calculate_best_layout(roof_left, panel_base, BORDER, obstacles_left, "portrait")
    # Спроба 2: Альбомна орієнтація як базова
    data_L_L = calculate_best_layout(roof_left, panel_base, BORDER, obstacles_left, "landscape")
    
    data_L = data_L_P if data_L_P["total_panels"] >= data_L_L["total_panels"] else data_L_L
    print(f"[LEFT ROOF] Best Layout: {data_L['total_panels']} panels. (P={data_L_P['total_panels']}, L={data_L_L['total_panels']})")

    # 3. Генерація та порівняння розкладок для ПРАВОГО даху

    data_R_P = calculate_best_layout(roof_right, panel_base, BORDER, obstacles_right, "portrait")
    data_R_L = calculate_best_layout(roof_right, panel_base, BORDER, obstacles_right, "landscape")
    
    data_R = data_R_P if data_R_P["total_panels"] >= data_R_L["total_panels"] else data_R_L
    print(f"[RIGHT ROOF] Best Layout: {data_R['total_panels']} panels. (P={data_R_P['total_panels']}, L={data_R_L['total_panels']})")
    
    print(f"[TOTAL] Panels placed: {data_L['total_panels'] + data_R['total_panels']}")


    # 4. Валідація
    try:
        assert_layout_valid(roof_left,  BORDER, data_L, obstacles_left)
        assert_layout_valid(roof_right, BORDER, data_R, obstacles_right)
        print("[CHECK] Collision tests: OK")
    except AssertionError as e:
        print(f"!!! [ERROR] VALIDATION FAILED: {e}")
        # Зупиняємося, якщо валідація не пройшла
        return


    # 5. Візуалізація та експорт
    png_path = os.path.join(cfg.out_dir, "top_view.png") if cfg.save_png else None
    
    # Використовуємо параметри панелі з обраного найкращого результату
    panel_for_plot = Panel(width=data_L["panel_w"], height=data_L["panel_h"],
                           gap_x=panel_base.gap_x, gap_y=panel_base.gap_y, clamp_margin=panel_base.clamp_margin)
    
    draw_two_roofs_columns(roof_left, roof_right, panel_for_plot, data_L, data_R,
                           obstacles_left=obstacles_left, obstacles_right=obstacles_right,
                           save_path=png_path, show=True)
    if png_path:
        print(f"[SAVE] PNG збережено у: {os.path.abspath(png_path)}")

    if cfg.save_csv:
        csv_L_path = os.path.join(cfg.out_dir, "panels_left.csv")
        csv_R_path = os.path.join(cfg.out_dir, "panels_right.csv")
        export_csv(csv_L_path, "L", data_L, panel_base)
        export_csv(csv_R_path, "R", data_R, panel_base)
        print(f"[SAVE] CSV збережено у: {os.path.abspath(cfg.out_dir)}")
    
    print("--- [END] Розрахунок 'Top View' завершено. ---")


if __name__ == "__main__":
    run_top_view_calculation()