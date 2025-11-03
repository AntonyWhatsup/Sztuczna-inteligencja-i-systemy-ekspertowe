import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def draw_side_view(ax, config=None, left_data=None, right_data=None, title="Вигляд збоку"):
    """
    Малює боковий вигляд двоскатного даху з панелями, димарем і вікном.

    Параметри:
        config: словник з параметрами даху (width, roof_height, roof_angle)
        left_data, right_data: (опціонально) дані панелей на лівому та правому схилах
        title: заголовок графіка
    """

    # --- Основні параметри ---
    width = 10000  # мм — ширина будинку
    roof_height = 2500  # мм — висота в коньку
    angle = np.radians(35)
    half_width = width / 2

    # --- Лінії даху ---
    left_roof_x = [0, half_width]
    left_roof_y = [0, roof_height]
    right_roof_x = [half_width, width]
    right_roof_y = [roof_height, 0]

    # Малюємо дах
    ax.plot(left_roof_x, left_roof_y, color="black", lw=2)
    ax.plot(right_roof_x, right_roof_y, color="black", lw=2)

    # Малюємо корпус будинку (основу)
    ax.plot([0, width], [0, 0], color="black", lw=2)

    # --- Димар ---
    chimney_base_x = width * 0.6
    chimney_base_y = roof_height - np.tan(angle) * (chimney_base_x - half_width)
    chimney_width = 400
    chimney_height = 1000
    ax.add_patch(
        patches.Rectangle(
            (chimney_base_x, chimney_base_y),
            chimney_width,
            chimney_height,
            color="gray",
            ec="black",
        )
    )

    # --- Вікно ---
    window_x = width * 0.3
    window_y = roof_height - np.tan(angle) * (half_width - window_x)
    ax.add_patch(
        patches.Rectangle(
            (window_x, window_y - 200),
            500,
            200,
            color="skyblue",
            ec="black",
        )
    )

    # --- Панелі (спрощено) ---
    def draw_panels_on_slope(base_x, base_y, side="left"):
        for i in range(3):
            px = base_x + (i * 600 if side == "right" else -i * 600)
            py = base_y + (i * np.tan(angle) * 600)
            ax.add_patch(
                patches.Rectangle(
                    (px, py),
                    500,
                    300,
                    angle=(-35 if side == "left" else 35),
                    color="orange",
                    ec="black",
                    lw=0.6,
                )
            )

    draw_panels_on_slope(half_width - 500, roof_height - 200, side="left")
    draw_panels_on_slope(half_width, roof_height - 200, side="right")

    # --- Параметри відображення ---
    ax.set_xlim(-500, width + 1000)
    ax.set_ylim(-500, roof_height + 1500)
    ax.set_aspect("equal")
    ax.set_title(title)
    ax.set_xlabel("Ширина (мм)")
    ax.set_ylabel("Висота (мм)")
    ax.grid(True, linestyle="--", alpha=0.5)


def visualize_side_view():
    """Окрема функція для запуску бокового вигляду як самостійного вікна."""
    fig, ax = plt.subplots(figsize=(8, 6))
    draw_side_view(ax)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_side_view()
