# panel.py
from typing import List, Tuple

class Panel:
    def __init__(self, width, height, gap_x=0, gap_y=0, clamp_margin=30):
        self.width = width
        self.height = height
        self.gap_x = gap_x
        self.gap_y = gap_y
        self.clamp_margin = clamp_margin

# ---------- GRID ----------
def _lattice_counts(L, W, m_x, m_y, gx, gy, w, h, align_x="center", align_y="center"):
    """
    Рахує сітку з урахуванням вирівнювання (align_x, align_y).
    align_y="top" означає вирівнювання до m_y (ближче до kalenicy)
    """
    L_eff = L - 2*m_x
    W_eff = W - 2*m_y
    if L_eff <= 0 or W_eff <= 0:
        return 0, 0, 0, 0.0, m_x, m_y
    nx = int((L_eff + gx)//(w + gx))
    ny = int((W_eff + gy)//(h + gy))
    N  = nx*ny
    
    # Розрахунок використаного простору та "залишку" (slack)
    used_L = nx*w + max(nx-1,0)*gx
    used_W = ny*h + max(ny-1,0)*gy
    slack_L = L_eff - used_L
    slack_W = W_eff - used_W

    # --- Нова логіка вирівнювання ---
    # По X (Długość)
    if align_x == "left":
        sx = m_x
    elif align_x == "right":
        sx = m_x + slack_L  # (L - m_x - used_L)
    else: # "center"
        sx = m_x + 0.5*slack_L

    # По Y (Odległość od kalenicy)
    if align_y == "top": # 'top' = біля 'kalenicy', y=m_y
        sy = m_y
    elif align_y == "bottom":
        sy = m_y + slack_W # (W - m_y - used_W)
    else: # "center"
        sy = m_y + 0.5*slack_W
    # --- Кінець нової логіки ---

    cov = (N*w*h)/(L_eff*W_eff) if L_eff>0 and W_eff>0 else 0.0
    return nx, ny, N, cov, sx, sy

def best_orientation(L, W, m_x, m_y, gx, gy, w_portrait=1000, h_portrait=1700):
    # Оцінюємо ТІЛЬКИ по центральному розміщенню, щоб обрати орієнтацію
    nx_p, ny_p, N_p, cov_p, *_ = _lattice_counts(L, W, m_x, m_y, gx, gy, w_portrait, h_portrait, "center", "center")
    nx_l, ny_l, N_l, cov_l, *_ = _lattice_counts(L, W, m_x, m_y, gx, gy, h_portrait, w_portrait, "center", "center")
    if N_l > N_p:
        return {"orientation":"landscape","w":h_portrait,"h":w_portrait,
                "nx":nx_l,"ny":ny_l,"N":N_l,"coverage_eff":cov_l}
    else:
        return {"orientation":"portrait","w":w_portrait,"h":h_portrait,
                "nx":nx_p,"ny":ny_p,"N":N_p,"coverage_eff":cov_p}

def fill_roof_with_panels(roof, panel, border_x=0, border_y=0, orientation="auto", 
                          align_x="center", align_y="center"):
    if orientation=="auto":
        # Якщо auto, запускаємо best_orientation, яка вже використовує 'center'
        ch = best_orientation(roof.length, roof.width, border_x, border_y,
                              panel.gap_x, panel.gap_y, panel.width, panel.height)
        w, h = ch["w"], ch["h"]; ori = ch["orientation"]
    else:
        if orientation=="portrait":
            w, h = panel.width, panel.height
        elif orientation=="landscape":
            w, h = panel.height, panel.width
        else:
            raise ValueError("orientation must be auto|portrait|landscape")
        ori = orientation
    
    # Передаємо параметри вирівнювання в _lattice_counts
    nx, ny, N, cov, sx, sy = _lattice_counts(roof.length, roof.width, border_x, border_y,
                                             panel.gap_x, panel.gap_y, w, h,
                                             align_x=align_x, align_y=align_y)
                                             
    return {"rows":ny,"cols":nx,"total_panels":N,"coverage_eff":cov,
            "border_x":border_x,"border_y":border_y,"start_x":sx,"start_y":sy,
            "panel_w":w,"panel_h":h,"orientation":ori}

# ---------- OBSTACLES (GRID mask) ----------
def _overlap(ax, ay, aw, ah, bx, by, bw, bh)->bool:
    return not (ax+aw<=bx or bx+bw<=ax or ay+ah<=by or by+bh<=ay)

def _inflate_rect_any(ob):
    if hasattr(ob, "inflated"):
        return ob.inflated()
    x,y,w,h = ob["x"], ob["y"], ob["w"], ob["h"]
    c = ob.get("clearance", 0.0)
    return (x-c, y-c, w+2*c, h+2*c)

def fill_with_obstacles(roof, panel, data, obstacles):
    sx, sy = data["start_x"], data["start_y"]
    nx, ny = data["cols"], data["rows"]
    w, h   = data["panel_w"], data["panel_h"]
    gx, gy = panel.gap_x, panel.gap_y
    masks = [_inflate_rect_any(ob) for ob in (obstacles or [])]
    placed: List[Tuple[float,float,float,float]] = []
    for r in range(ny):
        y = sy + r*(h+gy)
        for c in range(nx):
            x = sx + c*(w+gx)
            if all(not _overlap(x,y,w,h, mx,my,mw,mh) for (mx,my,mw,mh) in masks):
                placed.append((x,y,w,h))
    out = dict(data)
    out["placed_rects"] = placed
    out["total_panels"] = len(placed)
    return out

# ---------- POST: recenter + portrait columns ----------
def _inflate_rect_gap(rect, gx, gy):
    x,y,w,h = rect
    return (x-gx, y-gy, w+2*gx, h+2*gy)

def _can_place(x, y, w, h, masks):
    for (mx,my,mw,mh) in masks:
        if _overlap(x,y,w,h, mx,my,mw,mh):
            return False
    return True

# --- (Функції _recenter_grid, _edge_free_widths, _place_portrait_columns, 
# --- і augment_with_shifted_portrait більше не використовуються в main.py, 
# --- але ми можемо їх залишити, вони не заважають) ---

def _recenter_grid(data, roof, panel, side:str):
    m_x = data["border_x"]; gx = panel.gap_x
    w   = data["panel_w"];  nx = data["cols"]
    used_L = nx*w + max(nx-1,0)*gx
    sx = m_x if side=="left" else (roof.length - m_x - used_L)
    out = dict(data); out["start_x"] = sx
    return out

def _edge_free_widths(roof, data):
    bx = data["border_x"]; L = roof.length
    rects = data.get("placed_rects", [])
    if not rects:
        return 0.0, 0.0
    min_x = min(x for (x,_,w,_) in rects)
    max_x = max(x+w for (x,_,w,_) in rects)
    left  = max(0.0, min_x - bx)
    right = max(0.0, (L - bx) - max_x)
    return left, right

def _place_portrait_columns(side, roof, panel, data_with_rects, obstacles, max_cols):
    bx, by = data_with_rects["border_x"], data_with_rects["border_y"]
    L, W   = roof.length, roof.width
    gx, gy = panel.gap_x, panel.gap_y
    pw, ph = panel.width, panel.height  # portrait
    masks = []
    for ob in (obstacles or []):
        masks.append(_inflate_rect_any(ob))
    masks += [_inflate_rect_gap(r, gx, gy) for r in data_with_rects.get("placed_rects", [])]
    cols_x = [ (bx + i*(pw+gx)) if side=="left" else (L - bx - pw - i*(pw+gx)) for i in range(max_cols) ]
    best_added = []
    for y_off in (0.0, (ph+gy)/2.0):
        loc_masks = list(masks)
        added = []
        for xP in cols_x:
            y = by + y_off
            while y + ph <= W - by + 1e-9:
                if _can_place(xP, y, pw, ph, loc_masks):
                    added.append((xP, y, pw, ph))
                    loc_masks.append(_inflate_rect_gap((xP, y, pw, ph), gx, gy))
                y += ph + gy
        if len(added) > len(best_added):
            best_added = added
    return best_added

def augment_with_shifted_portrait(roof, panel, data, obstacles=None):
    # A: прижать влево → допаковать справа
    left_data  = fill_with_obstacles(roof, panel, _recenter_grid(data, roof, panel, "left"), obstacles)
    lf, rf = _edge_free_widths(roof, left_data)
    need = panel.width + panel.gap_x
    kR = int((rf + panel.gap_x)//(panel.width + panel.gap_x)) if rf >= need else 0
    add_R = _place_portrait_columns("right", roof, panel, left_data, obstacles, kR) if kR>0 else []
    total_A = left_data["total_panels"] + len(add_R)

    # B: прижать вправо → допаковать слева
    right_data = fill_with_obstacles(roof, panel, _recenter_grid(data, roof, panel, "right"), obstacles)
    lf, rf = _edge_free_widths(roof, right_data)
    kL = int((lf + panel.gap_x)//(panel.width + panel.gap_x)) if lf >= need else 0
    add_L = _place_portrait_columns("left", roof, panel, right_data, obstacles, kL) if kL>0 else []
    total_B = right_data["total_panels"] + len(add_L)

    if total_A >= total_B:
        out = dict(left_data)
        out["placed_rects"] = left_data["placed_rects"] + add_R
        out["total_panels"] = total_A
        out["note"] = f"recenter=left + portrait(right) +{len(add_R)} cols={kR}"
    else:
        out = dict(right_data)
        out["placed_rects"] = right_data["placed_rects"] + add_L
        out["total_panels"] = total_B
        out["note"] = f"recenter=right + portrait(left) +{len(add_L)} cols={kL}"
    return out


# --- gap scan: портретные панели в любых свободных коридорах по X ---
def _merge_intervals(intervals):
    xs = sorted(intervals)
    out = []
    for a, b in xs:
        if not out or a > out[-1][1]:
            out.append([a, b])
        else:
            out[-1][1] = max(out[-1][1], b)
    return [(a, b) for a, b in out]

def _free_intervals(base, blocks):
    a0, b0 = base
    merged = _merge_intervals([(max(a0, a), min(b0, b))
                               for a, b in blocks if b > a and not (b <= a0 or a >= b0)])
    free, cur = [], a0
    for a, b in merged:
        if a > cur: free.append((cur, a))
        cur = max(cur, b)
    if cur < b0: free.append((cur, b0))
    return free

def augment_with_gap_portraits(roof, panel, data, obstacles=None):
    """
    Після базового GRID+obstacles скануємо кожен «ряд по Y» і допаковуємо
    портретні панелі (1000x1700) в будь-які вільні інтервали по X.
    Пробуємо два вертикальних офсети: 0 і (h+gap)/2. Вибираємо найкращий.
    """
    bx, by = data["border_x"], data["border_y"]
    L, W   = roof.length, roof.width
    gx, gy = panel.gap_x, panel.gap_y
    pw, ph = panel.width, panel.height  # portrait

    # маски: перешкоди (inflated) + вже укладені панелі (розширені на gap)
    base_masks = []
    for ob in (obstacles or []):
        base_masks.append(_inflate_rect_any(ob))
    base_masks += [_inflate_rect_gap(r, gx, gy) for r in data.get("placed_rects", [])]

    best_added = []
    for y_off in (0.0, (ph + gy)/2.0):
        masks = list(base_masks)
        added = []
        y = by + y_off
        while y + ph <= W - by + 1e-9:
            # блокуючі інтервали по X для смуги [y, y+ph]
            blocks = []
            for (mx, my, mw, mh) in masks:
                if not (y + ph <= my or my + mh <= y):
                    blocks.append((mx, mx + mw))
            # вільні інтервали і укладання колонками
            for a, b in _free_intervals((bx, L - bx), blocks):
                length = b - a
                k = int((length + gx) // (pw + gx))
                if k <= 0: 
                    continue
                x0 = a  # вирівнюємо до лівого краю інтервалу
                for i in range(k):
                    x = x0 + i * (pw + gx)
                    if _can_place(x, y, pw, ph, masks):
                        added.append((x, y, pw, ph))
                        masks.append(_inflate_rect_gap((x, y, pw, ph), gx, gy))
            y += ph + gy
        if len(added) > len(best_added):
            best_added = added

    if not best_added:
        return data
    out = dict(data)
    out["placed_rects"] = list(data.get("placed_rects", [])) + best_added
    out["total_panels"] = len(out["placed_rects"])
    out["note"] = f"gap-portrait +{len(best_added)}"
    return out
