# main.py

from roof import Roof
from panel import Panel, fill_roof_with_panels
from formulas import efficiency, cost
from visualization import draw_roof  # опціонально, якщо хочеш візуалізацію

# --- Параметри ---
roof = Roof(width=5500, length=20000)   # мм
panel = Panel(width=1000, height=1700, gap_x=100, gap_y=100)

# --- Розрахунок ---
data = fill_roof_with_panels(roof, panel)

# --- Формули ---
total_power = efficiency(panel_power=400, total_panels=data["total_panels"])
total_cost = cost(data["total_panels"], cost_per_panel=800)

# --- Результат ---
print("=== Результати розміщення панелей ===")
print(f"Розмір даху: {roof.width} x {roof.length} мм")
print(f"Рядів: {data['rows']}  |  Колонок: {data['cols']}")
print(f"Кількість панелей: {data['total_panels']}")
print(f"Заповнена площа: {data['coverage']*100:.2f}%")
print(f"Сумарна потужність: {total_power/1000:.2f} kW")
print(f"Орієнтовна вартість: {total_cost:.2f} PLN")

# --- Візуалізація ---
draw_roof(roof, panel, data)
