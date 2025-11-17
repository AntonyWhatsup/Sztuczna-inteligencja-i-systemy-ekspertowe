# visualization_ea.py
"""
Evolutionary top-view for panel placement.
Run:  python visualization_ea.py

Algorithm:
- generates a set of potential "slots" for portrait and landscape orientations;
- each individual = a permutation of slots;
- greedy decoder iterates over the slots and places panels,
  if they do not exceed the border and do not collide with obstacles / other panels;
- objective function: maximize number of panels.
"""

import os
import random
from dataclasses import dataclass
from typing import List, Tuple

from config import Config
from roof import Roof
from panel import Panel, fill_roof_with_panels
from plotter_top_view import draw_two_roofs_columns
from project_utils import Obstacle, assert_layout_valid, export_csv, _overlap


# ---------- BASIC STRUCTURES ----------

@dataclass(frozen=True)
class Slot:
    side: str        # "L" or "R"
    x: float
    y: float
    w: float
    h: float
    orient: str      # "P" (portrait) or "L" (landscape)


# ---------- SLOT GENERATION ----------

def _generate_slots_for_side(
    side: str,
    roof: Roof,
    panel: Panel,
    border: int,
    obstacles: List[Obstacle]
) -> List[Slot]:
    """
    Generates all valid slots (portrait + landscape) that:
    - are inside the orange border (border),
    - do not intersect inflated obstacles.
    """
    slots: List[Slot] = []
    gx, gy = panel.gap_x, panel.gap_y
    inflated = [ob.inflated() for ob in obstacles]

    def scan_orientation(orient_name: str, orientation: str) -> None:
        data = fill_roof_with_panels(
            roof, panel,
            border_x=border, border_y=border,
            orientation=orientation
        )
        nx, ny = data["cols"], data["rows"]
        if nx <= 0 or ny <= 0:
            return

        w, h = data["panel_w"], data["panel_h"]
        sx, sy = data["start_x"], data["start_y"]

        for r in range(ny):
            y = sy + r * (h + gy)
            for c in range(nx):
                x = sx + c * (w + gx)

                # check obstacles
                bad = False
                for (mx, my, mw, mh) in inflated:
                    if _overlap(x, y, w, h, mx, my, mw, mh):
                        bad = True
                        break
                if bad:
                    continue

                slots.append(Slot(side=side, x=x, y=y, w=w, h=h, orient=orient_name))

    # portrait + landscape
    scan_orientation("P", "portrait")
    scan_orientation("L", "landscape")

    if not slots:
        raise RuntimeError(f"[{side}] No valid slot found. Check border/obstacles.")

    return slots


# ---------- DECODER AND FITNESS ----------

def _decode_individual(
    slots_order: List[Slot],
    roof: Roof,
    border: int,
    obstacles: List[Obstacle],
    panel: Panel,
) -> dict:
    """
    Greedy decoder: iterate over slots in given order,
    placing panels without collisions.
    """
    placed: List[Tuple[float, float, float, float]] = []
    inflated_obs = [ob.inflated() for ob in obstacles]

    L, W = roof.length, roof.width
    bx = by = border

    for s in slots_order:
        x, y, w, h = s.x, s.y, s.w, s.h

        # check border
        if not (x >= bx and y >= by and x + w <= L - bx and y + h <= W - by):
            continue

        # collision with already placed panels
        collision = False
        for (px, py, pw, ph) in placed:
            if _overlap(x, y, w, h, px, py, pw, ph):
                collision = True
                break
        if collision:
            continue

        # collision with obstacles (including clearance)
        for (mx, my, mw, mh) in inflated_obs:
            if _overlap(x, y, w, h, mx, my, mw, mh):
                collision = True
                break
        if collision:
            continue

        placed.append((x, y, w, h))

    # For top-view it's enough to pass placed_rects;
    # cols/rows are not used here.
    data = {
        "border_x": border,
        "border_y": border,
        "panel_w": panel.width,   # base size (for legend)
        "panel_h": panel.height,
        "cols": 0,
        "rows": 0,
        "start_x": border,
        "start_y": border,
        "placed_rects": placed,
        "total_panels": len(placed),
    }
    return data


def _fitness(data: dict) -> int:
    """Simple objective function: number of panels."""
    return int(data.get("total_panels", 0))


# ---------- GA OPERATORS ----------

def _order_crossover(parent1: List[Slot], parent2: List[Slot]) -> List[Slot]:
    """Order Crossover (OX) for permutations."""
    n = len(parent1)
    if n < 2:
        return parent1[:]
    a, b = sorted(random.sample(range(n), 2))
    child: List[Slot] = [None] * n  # type: ignore

    # segment from first parent
    child[a:b] = parent1[a:b]
    used = {s for s in child[a:b] if s is not None}

    # remaining slots in order from second parent
    j = b
    for s in parent2:
        if s in used:
            continue
        if j >= n:
            j = 0
        child[j] = s
        j += 1

    # type: ignore, but in fact all slots filled
    return child  # type: ignore


def _mutate_swap(ind: List[Slot], p_mut: float) -> None:
    """Simple mutation: swap two positions."""
    if len(ind) < 2:
        return
    if random.random() > p_mut:
        return
    i, j = random.sample(range(len(ind)), 2)
    ind[i], ind[j] = ind[j], ind[i]


# ---------- RUN GA FOR ONE ROOF SIDE ----------

def _run_ga_for_side(
    side: str,
    roof: Roof,
    panel: Panel,
    border: int,
    obstacles: List[Obstacle],
    n_generations: int = 10,
    pop_size: int = 30,
    p_mut: float = 0.2,
    elite_size: int = 2,
):
    """Run GA for one roof half (left / right)."""
    slots = _generate_slots_for_side(side, roof, panel, border, obstacles)
    print(f"[{side}] Available slots count: {len(slots)}")

    # initialize population
    population: List[List[Slot]] = [
        random.sample(slots, len(slots)) for _ in range(pop_size)
    ]

    best_data = None
    best_fit = -1

    for gen in range(n_generations):
        scored = []
        for ind in population:
            data = _decode_individual(ind, roof, border, obstacles, panel)
            f = _fitness(data)
            scored.append((f, ind, data))
            if f > best_fit:
                best_fit = f
                best_data = data

        scored.sort(key=lambda t: t[0], reverse=True)
        gen_best = scored[0][0]
        print(f"[{side}] Gen {gen+1}/{n_generations}: best={gen_best}, global_best={best_fit}")

        # elitism
        new_pop: List[List[Slot]] = [
            scored[i][1][:] for i in range(min(elite_size, len(scored)))
        ]

        # children
        while len(new_pop) < pop_size:
            p1 = random.choice(scored[: max(3, pop_size // 3)])[1]
            p2 = random.choice(scored[: max(3, pop_size // 3)])[1]
            child = _order_crossover(p1, p2)
            _mutate_swap(child, p_mut)
            new_pop.append(child)

        population = new_pop

    if best_data is None:
        raise RuntimeError(f"[{side}] GA finished with no solution, something went wrong.")

    return best_data


# ---------- MAIN FUNCTION ----------

def run_evolutionary_top_view(
    generations: int = 10,
    pop_size: int = 30,
):
    cfg = Config()
    BORDER = cfg.roof_left.border

    roof_left = Roof(width=cfg.roof_left.width, length=cfg.roof_left.length)
    roof_right = Roof(width=cfg.roof_right.width, length=cfg.roof_right.length)

    panel_base = Panel(
        width=cfg.panel.width,
        height=cfg.panel.height,
        gap_x=cfg.panel.gap_x,
        gap_y=cfg.panel.gap_y,
        clamp_margin=cfg.panel.clamp,
    )

    obstacles_left: List[Obstacle] = [Obstacle(**vars(o)) for o in cfg.obstacles_left]
    obstacles_right: List[Obstacle] = [Obstacle(**vars(o)) for o in cfg.obstacles_right]

    print("[GA] Starting evolutionary search for left side...")
    data_L = _run_ga_for_side(
        "L", roof_left, panel_base, BORDER, obstacles_left,
        n_generations=generations, pop_size=pop_size,
    )

    print("[GA] Starting evolutionary search for right side...")
    data_R = _run_ga_for_side(
        "R", roof_right, panel_base, BORDER, obstacles_right,
        n_generations=generations, pop_size=pop_size,
    )

    total_panels = data_L["total_panels"] + data_R["total_panels"]
    print(f"[GA] Summary: L={data_L['total_panels']} panels, "
          f"R={data_R['total_panels']} panels, total={total_panels}")

    # Validation to ensure no panel exceeds the ridge
    assert_layout_valid(roof_left, BORDER, data_L, obstacles_left)
    assert_layout_valid(roof_right, BORDER, data_R, obstacles_right)

    # Visualization
    png_path = None
    if cfg.save_png:
        png_path = os.path.join(cfg.out_dir, "ea_top_view.png")
        os.makedirs(cfg.out_dir, exist_ok=True)

    panel_for_plot = Panel(
        width=data_L["panel_w"],
        height=data_L["panel_h"],
        gap_x=panel_base.gap_x,
        gap_y=panel_base.gap_y,
        clamp_margin=panel_base.clamp_margin,
    )

    draw_two_roofs_columns(
        roof_left, roof_right,
        panel_for_plot,
        data_L, data_R,
        obstacles_left=obstacles_left,
        obstacles_right=obstacles_right,
        save_path=png_path,
        show=True,
    )

    if png_path:
        print(f"[SAVE] Evolutionary top-view saved to: {os.path.abspath(png_path)}")

    # CSV export (coordinates are correct, row/col for mixed orientation mostly nominal)
    if cfg.save_csv:
        csv_L = os.path.join(cfg.out_dir, "ea_panels_left.csv")
        csv_R = os.path.join(cfg.out_dir, "ea_panels_right.csv")
        export_csv(csv_L, "L", data_L, panel_base)
        export_csv(csv_R, "R", data_R, panel_base)
        print(f"[EXPORT] CSV for evolutionary layout saved in {cfg.out_dir}")


if __name__ == "__main__":
    # As per spec: run 10 generations.
    run_evolutionary_top_view(generations=10, pop_size=30)
