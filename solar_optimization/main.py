# main.py

from roof import Roof
from panel import Panel, fill_roof_with_panels
from formulas import efficiency, cost
from visualization import draw_two_separate_roofs  # нова функція

# --- Параметри ---
roof_left = Roof(width=5500, length=20000)
roof_right = Roof(width=5500, length=20000)

panel = Panel(width=1000, height=1700, gap_x=100, gap_y=100)

# --- Розрахунок окремо для кожного скосу ---
data_left = fill_roof_with_panels(roof_left, panel)
data_right = fill_roof_with_panels(roof_right, panel)

# --- Сумарні результати ---
total_panels = data_left["total_panels"] + data_right["total_panels"]
total_coverage = (data_left["coverage"] + data_right["coverage"]) / 2

# --- Формули ---
total_power = efficiency(panel_power=400, total_panels=total_panels)
total_cost = cost(total_panels, cost_per_panel=800)

# --- Вивід ---
print("=== ДВОСКАТНИЙ ДАХ ===")
print(f"Кожен скос: {roof_left.width} x {roof_left.length} мм")
print(f"Панелей (лівий скос): {data_left['total_panels']}")
print(f"Панелей (правий скос): {data_right['total_panels']}")
print(f"Разом панелей: {total_panels}")
print(f"Середнє заповнення: {total_coverage*100:.2f}%")
print(f"Загальна потужність: {total_power/1000:.2f} kW")
print(f"Орієнтовна вартість: {total_cost:.2f} PLN")

# --- Візуалізація двох окремих площин ---
draw_two_separate_roofs(roof_left, roof_right, panel, data_left, data_right)
