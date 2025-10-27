# main.py
from roof import Roof
from panel import Panel, fill_roof_with_panels
from formulas import efficiency, cost
from visualization import draw_two_mirrored_roofs

# --- Параметри ---
BORDER = 300  # Відступ від країв даху (мм)
roof_left = Roof(width=5500, length=20000)
roof_right = Roof(width=5500, length=20000)
panel = Panel(width=1000, height=1700, gap_x=100, gap_y=100)

# --- Розрахунок для обох площин ---
data_left = fill_roof_with_panels(roof_left, panel, border_x=BORDER, border_y=BORDER)
data_right = fill_roof_with_panels(roof_right, panel, border_x=BORDER, border_y=BORDER)

# --- Перевірка ---
if data_left["total_panels"] == 0 or data_right["total_panels"] == 0:
    print("⚠️ Панелі не помістились на дах через великі відступи або малі розміри!")

# --- Розрахунки ---
total_panels = data_left["total_panels"] + data_right["total_panels"]
total_coverage = (
    data_left["coverage"] * roof_left.width * roof_left.length +
    data_right["coverage"] * roof_right.width * roof_right.length
) / (roof_left.width * roof_left.length + roof_right.width * roof_right.length)

total_power = efficiency(panel_power=400, total_panels=total_panels)
total_cost = cost(total_panels, cost_per_panel=800)

# --- Вивід ---
print("=== ДВОСКАТНИЙ ДАХ ===")
print(f"Панелей (лівий скос): {data_left['total_panels']}")
print(f"Панелей (правий скос): {data_right['total_panels']}")
print(f"Разом панелей: {total_panels}")
print(f"Середнє заповнення: {total_coverage*100:.2f}%")
print(f"Загальна потужність: {total_power/1000:.2f} kW")
print(f"Орієнтовна вартість: {total_cost:.2f} PLN")

# --- Візуалізація ---
draw_two_mirrored_roofs(roof_left, roof_right, panel, data_left, data_right, border=BORDER)
