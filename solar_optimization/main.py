from roof import Roof
from panel import Panel, fill_roof_with_panels, best_orientation
from visualization import draw_two_roofs_columns

BORDER = 300  # margines wokół obwodu (mm) (відступ по периметру (мм))

# wymiary połaci dachu (każda) (розміри половин даху (кожна))
roof_left = Roof(width=5500, length=20000)
roof_right = Roof(width=5500, length=20000)

# panel i odstępy montażowe (панель і монтажні зазори)
panel_base = Panel(width=1000, height=1700, gap_x=100, gap_y=100, clamp_margin=30)

# wybór najlepszej orientacji po maksymalnej liczbie paneli N* (вибір найкращої орієнтації по максимуму N*)
choice = best_orientation(
    L=roof_left.length, W=roof_left.width,
    m_x=BORDER, m_y=BORDER,
    gx=panel_base.gap_x, gy=panel_base.gap_y,
    w_portrait=panel_base.width, h_portrait=panel_base.height
)
print(f"ORIENTATION={choice['orientation']}; nx={choice['nx']} ny={choice['ny']} N*={choice['N']} "
      f"coverage={choice['coverage_eff']*100:.2f}%")

# rozkłady dla obu połaci z wybraną orientacją (розкладки для обох половин з обраною орієнтацією)
data_left = fill_roof_with_panels(roof_left, panel_base, BORDER, BORDER, orientation=choice["orientation"])
data_right = fill_roof_with_panels(roof_right, panel_base, BORDER, BORDER, orientation=choice["orientation"])

# panel z rzeczywistymi wymiarami po wyborze orientacji (do rysowania) (панель з реальними розмірами після вибору орієнтації (для відображення))
panel_for_plot = Panel(
    width=data_left["panel_w"], height=data_left["panel_h"],
    gap_x=panel_base.gap_x, gap_y=panel_base.gap_y, clamp_margin=panel_base.clamp_margin
)

# wizualizacja w dwóch „kolumnach” ze skalą 0..5500 mm dla każdej (візуалізація у двох «колонках» зі шкалою 0..5500 мм у кожній)
draw_two_roofs_columns(roof_left, roof_right, panel_for_plot, data_left, data_right)