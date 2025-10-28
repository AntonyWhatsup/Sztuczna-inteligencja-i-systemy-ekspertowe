# panel.py
import math

class Panel:
    """Параметры панели и монтажных зазоров."""
    def __init__(self, width, height, gap_x=0, gap_y=0, clamp_margin=30):
        self.width = width
        self.height = height
        self.gap_x = gap_x
        self.gap_y = gap_y
        self.clamp_margin = clamp_margin



def _lattice_counts(L, W, m_x, m_y, gx, gy, w, h):
    """Этап 1: решётчатая укладка. Возвращает nx, ny, N, coverage_eff, и стартовые координаты
    с симметричным центрированием внутри рамки."""
    L_eff = L - 2 * m_x
    W_eff = W - 2 * m_y
    if L_eff <= 0 or W_eff <= 0:
        return 0, 0, 0, 0.0, m_x, m_y

    nx = int((L_eff + gx) // (w + gx))
    ny = int((W_eff + gy) // (h + gy))
    N = nx * ny

    used_L = nx * w + max(nx - 1, 0) * gx
    used_W = ny * h + max(ny - 1, 0) * gy
    start_x = m_x + 0.5 * (L_eff - used_L)
    start_y = m_y + 0.5 * (W_eff - used_W)

    coverage_eff = (N * w * h) / (L_eff * W_eff) if L_eff > 0 and W_eff > 0 else 0.0
    return nx, ny, N, coverage_eff, start_x, start_y


def best_orientation(L, W, m_x, m_y, gx, gy, w_portrait=1000, h_portrait=1700):
    """Выбор портрет/альбом по максимальному N*."""
    # portrait
    nx_p, ny_p, N_p, cov_p, _, _ = _lattice_counts(L, W, m_x, m_y, gx, gy, w_portrait, h_portrait)
    # landscape
    nx_l, ny_l, N_l, cov_l, _, _ = _lattice_counts(L, W, m_x, m_y, gx, gy, h_portrait, w_portrait)

    if N_l > N_p:
        return {
            "orientation": "landscape",
            "w": h_portrait, "h": w_portrait,
            "nx": nx_l, "ny": ny_l, "N": N_l, "coverage_eff": cov_l
        }
    else:
        return {
            "orientation": "portrait",
            "w": w_portrait, "h": h_portrait,
            "nx": nx_p, "ny": ny_p, "N": N_p, "coverage_eff": cov_p
        }


def fill_roof_with_panels(roof, panel, border_x=0, border_y=0, orientation="auto"):
    """Возвращает раскладку для одной połaci с учётом ориентации.
       orientation ∈ {"auto","portrait","landscape"}."""
    if orientation == "auto":
        choice = best_orientation(
            roof.length, roof.width, border_x, border_y,
            panel.gap_x, panel.gap_y, panel.width, panel.height
        )
        w, h = choice["w"], choice["h"]
        nx, ny, N, cov, start_x, start_y = _lattice_counts(
            roof.length, roof.width, border_x, border_y,
            panel.gap_x, panel.gap_y, w, h
        )
        ori = choice["orientation"]
    else:
        if orientation == "portrait":
            w, h = panel.width, panel.height
        elif orientation == "landscape":
            w, h = panel.height, panel.width
        else:
            raise ValueError("orientation must be auto|portrait|landscape")
        nx, ny, N, cov, start_x, start_y = _lattice_counts(
            roof.length, roof.width, border_x, border_y,
            panel.gap_x, panel.gap_y, w, h
        )
        ori = orientation

    return {
        "rows": ny,
        "cols": nx,
        "total_panels": N,
        "coverage_eff": cov,
        "border_x": border_x,
        "border_y": border_y,
        "start_x": start_x,
        "start_y": start_y,
        "panel_w": w,
        "panel_h": h,
        "orientation": ori
    }
