# project_utils.py
import os
import csv
from dataclasses import dataclass
from typing import List, Tuple

# ! FIX: Import moved here, to the top of the file
from panel import Panel

# Local obstacle class for rendering and inflated()
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
    # borders
    for (x, y, w, h) in rects:
        if not (x >= bx and y >= by and x + w <= L - bx and y + h <= W - by):
            raise AssertionError(f"Panel out of border: {(x,y,w,h)}")
        if w <= 0 or h <= 0:
            raise AssertionError(f"Degenerate panel: {(x,y,w,h)}")
    # obstacles
    masks = [ob.inflated() for ob in obstacles]
    for (x, y, w, h) in rects:
        for (mx, my, mw, mh) in masks:
            if _overlap(x, y, w, h, mx, my, mw, mh):
                raise AssertionError(f"Collision with obstacle at {(mx,my,mw,mh)} by {(x,y,w,h)}")

# ---------- CSV export ----------
# Now the annotation 'panel: Panel' works correctly
def export_csv(path: str, side: str, data, panel: Panel):
    
    # ! FIX: This import is no longer needed (removed)
    # from panel import Panel 
    
    # ensure directory exists
    if os.path.dirname(path):
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
