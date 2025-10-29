import os, csv
from panel import Panel, best_orientation, fill_roof_with_panels, fill_with_obstacles, augment_with_gap_portraits

from dataclasses import dataclass
from typing import List, Tuple

from config import Config
from roof import Roof
from panel import Panel, best_orientation, fill_roof_with_panels, fill_with_obstacles
from visualization import draw_two_roofs_columns

# Локальный класс препятствия для рендера и inflated()
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

# ---------- валидатор раскладки ----------
def _overlap(ax, ay, aw, ah, bx, by, bw, bh) -> bool:
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)

def assert_layout_valid(roof, border, data, obstacles: List[Obstacle]) -> None:
    L, W = roof.length, roof.width
    bx, by = border, border
    rects = data.get("placed_rects", [])
    # границы
    for (x, y, w, h) in rects:
        if not (x >= bx and y >= by and x + w <= L - bx and y + h <= W - by):
            raise AssertionError(f"Panel out of border: {(x,y,w,h)}")
        if w <= 0 or h <= 0:
            raise AssertionError(f"Degenerate panel: {(x,y,w,h)}")
    # препятствия
    masks = [ob.inflated() for ob in obstacles]
    for (x, y, w, h) in rects:
        for (mx, my, mw, mh) in masks:
            if _overlap(x, y, w, h, mx, my, mw, mh):
                raise AssertionError(f"Collision with obstacle at {(mx,my,mw,mh)} by {(x,y,w,h)}")

# ---------- экспорт CSV ----------
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

# ---------- основной запуск ----------
if __name__ == "__main__":
    cfg = Config()  # конфигурация этапа 2

    # геометрия
    roof_left  = Roof(width=cfg.roof_left.width,  length=cfg.roof_left.length)
    roof_right = Roof(width=cfg.roof_right.width, length=cfg.roof_right.length)
    BORDER = cfg.roof_left.border  # одинаковый для обеих połaci

    # панель
    panel_base = Panel(width=cfg.panel.width, height=cfg.panel.height,
                       gap_x=cfg.panel.gap_x, gap_y=cfg.panel.gap_y, clamp_margin=cfg.panel.clamp)

    # препятствия из конфига
    obstacles_left = [Obstacle(**vars(o)) for o in cfg.obstacles_left]
    obstacles_right = [Obstacle(**vars(o)) for o in cfg.obstacles_right]

    # выбор ориентации
    choice = best_orientation(L=roof_left.length, W=roof_left.width,
                              m_x=BORDER, m_y=BORDER,
                              gx=panel_base.gap_x, gy=panel_base.gap_y,
                              w_portrait=panel_base.width, h_portrait=panel_base.height)
    print(f"[CONFIG] orientation={choice['orientation']}, "
          f"nx={choice['nx']}, ny={choice['ny']}, N*={choice['N']}, "
          f"coverage_eff={choice['coverage_eff']*100:.2f}%")

    # базовая решётка + маски препятствий
    base_L = fill_roof_with_panels(roof_left,  panel_base, BORDER, BORDER, orientation=choice["orientation"])
    base_R = fill_roof_with_panels(roof_right, panel_base, BORDER, BORDER, orientation=choice["orientation"])
    data_L = fill_with_obstacles(roof_left,  panel_base, base_L, obstacles_left)
    data_R = fill_with_obstacles(roof_right, panel_base, base_R, obstacles_right)
    data_L = augment_with_gap_portraits(roof_left,  panel_base, data_L, obstacles_left)
    data_R = augment_with_gap_portraits(roof_right, panel_base, data_R, obstacles_right)


    # валидация
    assert_layout_valid(roof_left,  BORDER, data_L, obstacles_left)
    assert_layout_valid(roof_right, BORDER, data_R, obstacles_right)
    print("[CHECK] collision tests: OK")

    # визуализация → PNG
    png_path = os.path.join(cfg.out_dir, "top_view.png") if cfg.save_png else None
    panel_for_plot = Panel(width=data_L["panel_w"], height=data_L["panel_h"],
                           gap_x=panel_base.gap_x, gap_y=panel_base.gap_y, clamp_margin=panel_base.clamp_margin)
    draw_two_roofs_columns(roof_left, roof_right, panel_for_plot, data_L, data_R,
                           obstacles_left=obstacles_left, obstacles_right=obstacles_right,
                           save_path=png_path, show=True)

    # CSV координаты
    if cfg.save_csv:
        export_csv(os.path.join(cfg.out_dir, "panels_left.csv"),  "L", data_L, panel_for_plot)
        export_csv(os.path.join(cfg.out_dir, "panels_right.csv"), "R", data_R, panel_for_plot)
        print("[EXPORT] CSV saved in", cfg.out_dir)
