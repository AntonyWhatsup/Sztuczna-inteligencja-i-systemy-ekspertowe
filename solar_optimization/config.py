# config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class RoofCfg:
    width: int = 5500
    length: int = 20000
    border: int = 300  # mm

@dataclass
class PanelCfg:
    width: int = 1000
    height: int = 1700
    gap_x: int = 100
    gap_y: int = 100
    clamp: int = 30

@dataclass
class ObstacleCfg:
    side: str
    x: float; y: float; w: float; h: float
    clearance: float = 100.0
    elev: float = 0.0
    type: str = "generic"    # "window"|"chimney"|"generic"
    frame_t: float = 80.0    # window
    grid_cols: int = 2
    grid_rows: int = 3
    cap_over: float = 80.0   # chimney

@dataclass
class Config:
    roof_left:  RoofCfg  = field(default_factory=RoofCfg)
    roof_right: RoofCfg  = field(default_factory=RoofCfg)
    panel:      PanelCfg = field(default_factory=PanelCfg)

    obstacles_left: List[ObstacleCfg] = field(default_factory=lambda: [
        ObstacleCfg(side="L", x=5000, y=2870, w=780, h=1180,
                    clearance=100, type="window", frame_t=80, grid_cols=2, grid_rows=3)
    ])
    obstacles_right: List[ObstacleCfg] = field(default_factory=lambda: [
        ObstacleCfg(side="R", x=10000, y=1350, w=400, h=270,
                    clearance=200, elev=500, type="chimney", cap_over=80)
    ])

    # ВАЖЛИВО: Змінено "out" на "results" для інтеграції з GUI
    out_dir: str = "results"
    save_png: bool = True
    save_csv: bool = True