import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw_side_view(ax, title="Side View"):
    """
    Draws a detailed side view of a gable roof,
    simulating a technical drawing.
    """

    # --- 1. Configuration parameters ---
    # We can move them to config.py later,
    # but for clarity they are here for now.

    # House parameters
    HOUSE_WIDTH = 10000     # mm (House width)
    WALL_HEIGHT = 2800      # mm (Wall height up to roof start)
    HOUSE_BASE_Y = 0        # (0,0 - bottom-left corner of the wall)

    # Roof parameters
    ROOF_ANGLE_DEG = 35     # Degrees
    ROOF_ANGLE_RAD = np.radians(ROOF_ANGLE_DEG)
    ROOF_THICKNESS = 250    # mm (Thickness of roof beams)
    
    # Computed parameters
    HALF_WIDTH = HOUSE_WIDTH / 2
    # Roof peak height (from wall top to ridge)
    ROOF_PEAK_HEIGHT = HALF_WIDTH * np.tan(ROOF_ANGLE_RAD) # ~3501 mm
    
    # Main coordinate points of the house
    P_WALL_L_BOT = (0, HOUSE_BASE_Y)
    P_WALL_L_TOP = (0, WALL_HEIGHT)
    P_WALL_R_BOT = (HOUSE_WIDTH, HOUSE_BASE_Y)
    P_WALL_R_TOP = (HOUSE_WIDTH, WALL_HEIGHT)
    P_ROOF_PEAK = (HALF_WIDTH, WALL_HEIGHT + ROOF_PEAK_HEIGHT)

    # --- 2. Helper functions to calculate Y on the slope ---
    
    # Equation of line (y = mx + c) for each slope
    # Left slope (L)
    m_L = (P_ROOF_PEAK[1] - P_WALL_L_TOP[1]) / (P_ROOF_PEAK[0] - P_WALL_L_TOP[0])
    c_L = P_ROOF_PEAK[1] - m_L * P_ROOF_PEAK[0]
    
    # Right slope (R)
    m_R = (P_ROOF_PEAK[1] - P_WALL_R_TOP[1]) / (P_ROOF_PEAK[0] - P_WALL_R_TOP[0])
    c_R = P_ROOF_PEAK[1] - m_R * P_ROOF_PEAK[0]

    def get_y_on_slope(x):
        """Returns 'y' on the roof surface for a given 'x'."""
        if x <= P_ROOF_PEAK[0]: # Left slope
            return m_L * x + c_L
        else: # Right slope
            return m_R * x + c_R

    # --- 3. Draw house structure ---
    
    # Walls
    ax.plot([P_WALL_L_BOT[0], P_WALL_L_TOP[0]], [P_WALL_L_BOT[1], P_WALL_L_TOP[1]], color="black", lw=2)
    ax.plot([P_WALL_R_BOT[0], P_WALL_R_TOP[0]], [P_WALL_R_BOT[1], P_WALL_R_TOP[1]], color="black", lw=2)
    # Base
    ax.axhline(HOUSE_BASE_Y, color="black", lw=2)
    # Ceiling line
    ax.plot([P_WALL_L_TOP[0], P_WALL_R_TOP[0]], [P_WALL_L_TOP[1], P_WALL_R_TOP[1]], color="gray", lw=1, linestyle='--')

    # Draw roof with thickness (as Polygon)
    offset_x = ROOF_THICKNESS * np.sin(ROOF_ANGLE_RAD)
    offset_y = ROOF_THICKNESS * np.cos(ROOF_ANGLE_RAD)

    # Left roof beam
    L_p1 = P_WALL_L_TOP
    L_p2 = P_ROOF_PEAK
    L_p3 = (P_ROOF_PEAK[0] + offset_x, P_ROOF_PEAK[1] - offset_y)
    L_p4 = (P_WALL_L_TOP[0] + offset_x, P_WALL_L_TOP[1] - offset_y)
    ax.add_patch(patches.Polygon([L_p1, L_p2, L_p3, L_p4], closed=True, color="#f0f0f0", ec="black", lw=1))

    # Right roof beam
    R_p1 = P_WALL_R_TOP
    R_p2 = P_ROOF_PEAK
    R_p3 = (P_ROOF_PEAK[0] - offset_x, P_ROOF_PEAK[1] - offset_y)
    R_p4 = (P_WALL_R_TOP[0] - offset_x, P_WALL_R_TOP[1] - offset_y)
    ax.add_patch(patches.Polygon([R_p1, R_p2, R_p3, R_p4], closed=True, color="#f0f0f0", ec="black", lw=1))

    # --- 4. Draw chimney ---
    # Chimney stands vertically. Its base "cuts" into the roof.
    chimney_x = HOUSE_WIDTH * 0.65
    chimney_width = 400
    chimney_height_above_roof = 1000

    y_base_left = get_y_on_slope(chimney_x)
    y_base_right = get_y_on_slope(chimney_x + chimney_width)
    
    C_p1 = (chimney_x, y_base_left)
    C_p2 = (chimney_x, y_base_left + chimney_height_above_roof)
    C_p3 = (chimney_x + chimney_width, y_base_right + chimney_height_above_roof)
    C_p4 = (chimney_x + chimney_width, y_base_right)
    
    ax.add_patch(patches.Polygon([C_p1, C_p2, C_p3, C_p4], closed=True, color="gray", ec="black", lw=1))

    # --- 5. Draw roof window ---
    window_x = HOUSE_WIDTH * 0.3
    window_width = 500
    window_height = 700
    
    win_offset_x = 50 * np.sin(ROOF_ANGLE_RAD)
    win_offset_y = 50 * np.cos(ROOF_ANGLE_RAD)
    
    W_p1 = (window_x, get_y_on_slope(window_x))
    W_p2_x = W_p1[0] + window_width * np.cos(ROOF_ANGLE_RAD)
    W_p2_y = W_p1[1] + window_width * np.sin(ROOF_ANGLE_RAD)
    
    W_p3_x = W_p2_x - win_offset_x
    W_p3_y = W_p2_y - win_offset_y
    W_p4_x = W_p1[0] - win_offset_x
    W_p4_y = W_p1[1] - win_offset_y

    y_win_base = get_y_on_slope(window_x)
    ax.add_patch(patches.Rectangle(
        (window_x, y_win_base - 50), # slightly below roof line
        window_width,
        50,
        color="skyblue",
        ec="black",
        lw=1,
        angle=ROOF_ANGLE_DEG,
        rotation_point="xy"
    ))

    # --- 6. Helper function to draw panels ---
    def draw_flush_panel(ax, x_start_on_wall, panel_length, mount_height, panel_thickness, slope_side):
        """Draws one flush-mounted panel on rails"""
        if slope_side == 'left':
            angle_rad = ROOF_ANGLE_RAD
            m = m_L
            c = c_L
            offset_x = -mount_height * np.sin(angle_rad)
            offset_y = mount_height * np.cos(angle_rad)
        else:
            angle_rad = -ROOF_ANGLE_RAD
            m = m_R
            c = c_R
            offset_x = -mount_height * np.sin(angle_rad)
            offset_y = mount_height * np.cos(angle_rad)

        x_base = x_start_on_wall
        y_base = m * x_base + c

        p_rail_1_base = (x_base, y_base)
        p_rail_1_top = (x_base + offset_x, y_base + offset_y)
        ax.plot([p_rail_1_base[0], p_rail_1_top[0]], [p_rail_1_base[1], p_rail_1_top[1]], color="black", lw=1)
        
        x_end = x_base + panel_length * np.cos(angle_rad)
        y_end = y_base + panel_length * np.sin(angle_rad)
        p_rail_2_base = (x_end, y_end)
        p_rail_2_top = (x_end + offset_x, y_end + offset_y)
        ax.plot([p_rail_2_base[0], p_rail_2_top[0]], [p_rail_2_base[1], p_rail_2_top[1]], color="black", lw=1)
        
        panel_off_x = -panel_thickness * np.sin(angle_rad)
        panel_off_y = panel_thickness * np.cos(angle_rad)

        P1 = p_rail_1_top
        P2 = p_rail_2_top
        P3 = (P2[0] + panel_off_x, P2[1] + panel_off_y)
        P4 = (P1[0] + panel_off_x, P1[1] + panel_off_y)
        
        ax.add_patch(patches.Polygon([P1, P2, P3, P4], closed=True, color="orange", ec="black", lw=1))

    # --- 7. Draw panels ---
    PANEL_LENGTH = 1700
    PANEL_THICKNESS = 40
    PANEL_MOUNT_HEIGHT = 100

    draw_flush_panel(ax, 1500, PANEL_LENGTH, PANEL_MOUNT_HEIGHT, PANEL_THICKNESS, 'left')
    draw_flush_panel(ax, 3300, PANEL_LENGTH, PANEL_MOUNT_HEIGHT, PANEL_THICKNESS, 'left')
    draw_flush_panel(ax, 5500, PANEL_LENGTH, PANEL_MOUNT_HEIGHT, PANEL_THICKNESS, 'right')
    draw_flush_panel(ax, 7300, PANEL_LENGTH, PANEL_MOUNT_HEIGHT, PANEL_THICKNESS, 'right')

    # --- 8. Plot settings ---
    ax.set_aspect("equal")
    ax.set_title(title)
    ax.set_xlabel("Width (mm)")
    ax.set_ylabel("Height (mm)")
    ax.grid(True, linestyle="--", alpha=0.5)
    
    ax.set_xlim(-500, HOUSE_WIDTH + 500)
    ax.set_ylim(-500, WALL_HEIGHT + ROOF_PEAK_HEIGHT + 1500)


def visualize_side_view():
    """
    Function to launch side view and save result in 'results' folder.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    draw_side_view(ax)
    plt.tight_layout()

    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "side_view.png")
    try:
        fig.savefig(output_path, dpi=200)
        print(f"💾 Graph saved at: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Error saving file: {e}")

    plt.show()


if __name__ == "__main__":
    visualize_side_view()
