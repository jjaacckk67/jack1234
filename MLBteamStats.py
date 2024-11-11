import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Path to the folder containing MLB team logos
logo_folder_path = "MLB LOGOS"

# Define the team abbreviation-to-full-name mapping for all 30 MLB teams
team_map = {
    "NYY": "New York Yankees", "BOS": "Boston Red Sox", "LAD": "Los Angeles Dodgers",
    "CHC": "Chicago Cubs", "ATL": "Atlanta Braves", "HOU": "Houston Astros",
    "PHI": "Philadelphia Phillies", "STL": "St. Louis Cardinals", "SF": "San Francisco Giants",
    "WSH": "Washington Nationals", "NYM": "New York Mets", "TOR": "Toronto Blue Jays",
    "MIL": "Milwaukee Brewers", "MIN": "Minnesota Twins", "TBR": "Tampa Bay Rays",
    "CLE": "Cleveland Guardians", "CIN": "Cincinnati Reds", "COL": "Colorado Rockies",
    "SEA": "Seattle Mariners", "SD": "San Diego Padres", "PIT": "Pittsburgh Pirates",
    "BAL": "Baltimore Orioles", "OAK": "Oakland Athletics", "KCR": "Kansas City Royals",
    "TEX": "Texas Rangers", "DET": "Detroit Tigers", "LAA": "Los Angeles Angels",
    "ARI": "Arizona Diamondbacks", "MIA": "Miami Marlins", "CWS": "Chicago White Sox"
}

# Load data from both sheets in the Excel file
data_hitting = pd.read_excel("your_baseball_data.csv.xlsx", sheet_name="Hitting")
data_pitching = pd.read_excel("your_baseball_data.csv.xlsx", sheet_name="Pitching")

# Create lists of available stats, sorted alphabetically
team_abbr = data_hitting['Team'] if 'Team' in data_hitting.columns else None
hitting_stats = sorted([col for col in data_hitting.columns if col != 'Team'])
pitching_stats = sorted([col for col in data_pitching.columns if col != 'Team'])

# Initialize a larger figure for better visibility
fig, ax = plt.subplots(figsize=(12, 8))  # Larger graph for more space
fig.patch.set_facecolor('#f4f4f8')
ax.set_title("MLB Stats Visualizer", fontsize=18, fontweight="bold", color="#333")
ax.set_xlabel("X Axis", fontsize=13, color="#555")
ax.set_ylabel("Y Axis", fontsize=13, color="#555")

# Store the hover label and annotation boxes for logos
annotation_boxes = []
hover_label = None
dragging = False
start_pos = None


# Function to plot the graph using logos and tooltips
def plot_stat(x_stat_hitting, x_stat_pitching, y_stat_hitting, y_stat_pitching):
    ax.clear()
    annotation_boxes.clear()

    # Validate that a valid stat is selected for both X and Y axes
    if x_stat_hitting == "Select statistic" and x_stat_pitching == "Select statistic":
        messagebox.showwarning("Invalid Selection", "Please select a valid stat for the X axis.")
        return

    if y_stat_hitting == "Select statistic" and y_stat_pitching == "Select statistic":
        messagebox.showwarning("Invalid Selection", "Please select a valid stat for the Y axis.")
        return

    # Create DataFrame based on selected stats
    plot_data = pd.DataFrame({
        'Team': team_abbr,
        'x_stat': data_hitting[x_stat_hitting] if x_stat_hitting != "Select statistic" else data_pitching[
            x_stat_pitching],
        'y_stat': data_hitting[y_stat_hitting] if y_stat_hitting != "Select statistic" else data_pitching[
            y_stat_pitching]
    }).dropna()

    if plot_data.empty:
        messagebox.showerror("Error", "No valid data for the selected stats.")
        return

    # Normalize the data for better scaling
    plot_data['x_stat'] = plot_data['x_stat'].apply(
        lambda x: x if x_stat_hitting not in ["Batting Average", "On Base Percentage", "Slugging Percentage",
                                              "OPS"] else (x - plot_data['x_stat'].min()) / (
                    plot_data['x_stat'].max() - plot_data['x_stat'].min()))
    plot_data['y_stat'] = plot_data['y_stat'].apply(
        lambda y: y if y_stat_hitting not in ["Batting Average", "On Base Percentage", "Slugging Percentage",
                                              "OPS"] else (y - plot_data['y_stat'].min()) / (
                    plot_data['y_stat'].max() - plot_data['y_stat'].min()))

    # Calculate the means for quadrant separation
    x_mean = plot_data['x_stat'].mean()
    y_mean = plot_data['y_stat'].mean()

    # Define plot limits to create extra space for logos
    ax.set_xlim(plot_data['x_stat'].min() - 0.05, plot_data['x_stat'].max() + 0.05)
    ax.set_ylim(plot_data['y_stat'].min() - 0.05, plot_data['y_stat'].max() + 0.05)

    # Add lighter grid lines (thinner and lighter in color than the axis lines)
    ax.grid(True, which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)

    # Plot team logos
    for i, abbr in plot_data['Team'].items():
        x_value = plot_data['x_stat'].iloc[i]
        y_value = plot_data['y_stat'].iloc[i]

        # Map abbreviation to full team name and logo
        team_name = team_map.get(abbr)
        if team_name:
            logo_file = f"mlb-{team_name.lower().replace(' ', '-')}-logo-300x300.png"
            logo_path = os.path.join(logo_folder_path, logo_file)

            if os.path.exists(logo_path):
                logo = plt.imread(logo_path)
                imagebox = OffsetImage(logo, zoom=0.1)  # Better quality zoom
                ab = AnnotationBbox(imagebox, (x_value, y_value), frameon=False)
                ax.add_artist(ab)

                # Set the stat name instead of the X/Y axis label in the tooltip
                x_stat_name = x_stat_hitting if x_stat_hitting != "Select statistic" else x_stat_pitching
                y_stat_name = y_stat_hitting if y_stat_hitting != "Select statistic" else y_stat_pitching

                # Store each logo's annotation and data for hover and click
                label = f"Team: {team_name}\n{y_stat_name}: {y_value:.2f}\n{x_stat_name}: {x_value:.2f}"
                annotation_boxes.append((ab, label))

    # Add quadrant lines
    ax.axhline(y=y_mean, color='gray', linestyle='--', linewidth=1)
    ax.axvline(x=x_mean, color='gray', linestyle='--', linewidth=1)

    fig.canvas.draw()

    # Connect hover, pan, and zoom events
    fig.canvas.mpl_connect("motion_notify_event", on_hover)
    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("button_release_event", on_release)
    fig.canvas.mpl_connect("scroll_event", on_zoom)


# Hover functionality
def on_hover(event):
    global hover_label
    if hover_label:
        hover_label.remove()
        hover_label = None
        fig.canvas.draw_idle()  # Refresh canvas to remove label

    for ab, label in annotation_boxes:
        contains, _ = ab.contains(event)
        if contains:
            hover_label = ax.text(event.xdata, event.ydata, label, ha="center", va="center",
                                  bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.8))
            fig.canvas.draw_idle()
            return  # Only show one label at a time


# Click functionality
def on_click(event):
    global hover_label
    if hover_label:
        hover_label.remove()  # Remove the current hover label
        hover_label = None
    else:
        for ab, label in annotation_boxes:
            contains, _ = ab.contains(event)
            if contains:
                hover_label = ax.text(event.xdata, event.ydata, label, ha="center", va="center",
                                      bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.8))
                fig.canvas.draw_idle()


# Handling panning on the plot
def on_press(event):
    global dragging, start_pos
    if event.button == MouseButton.LEFT:
        dragging = True
        start_pos = event.xdata, event.ydata


def on_release(event):
    global dragging
    dragging = False


def on_motion(event):
    global dragging, start_pos
    if dragging:
        dx = start_pos[0] - event.xdata
        dy = start_pos[1] - event.ydata
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        ax.set_xlim(cur_xlim + dx)
        ax.set_ylim(cur_ylim + dy)
        fig.canvas.draw_idle()  # Only update the canvas when necessary for smoother performance


# Zoom functionality
def on_zoom(event):
    scale_factor = 1.2
    if event.button == 'up':  # Zoom in
        scale = 1 / scale_factor
    elif event.button == 'down':  # Zoom out
        scale = scale_factor
    else:
        return

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xdata, ydata = event.xdata, event.ydata

    new_width = (xlim[1] - xlim[0]) * scale
    new_height = (ylim[1] - ylim[0]) * scale

    ax.set_xlim([xdata - new_width / 2, xdata + new_width / 2])
    ax.set_ylim([ydata - new_height / 2, ydata + new_height / 2])
    fig.canvas.draw_idle()


# Define the callback function for the "Generate Plot" button
def plot_button_click():
    selected_x_stat_hitting = dropdown_x_hitting.get()
    selected_x_stat_pitching = dropdown_x_pitching.get()
    selected_y_stat_hitting = dropdown_y_hitting.get()
    selected_y_stat_pitching = dropdown_y_pitching.get()

    # Ensure that at least one stat is selected from hitting and one from pitching for both axes
    if selected_x_stat_hitting == "Select statistic" and selected_x_stat_pitching == "Select statistic":
        messagebox.showwarning("Invalid Selection", "Please select a valid stat for the X axis.")
        return

    if selected_y_stat_hitting == "Select statistic" and selected_y_stat_pitching == "Select statistic":
        messagebox.showwarning("Invalid Selection", "Please select a valid stat for the Y axis.")
        return

    # Ensure at least one stat from hitting and one from pitching is selected for the axes
    if (selected_x_stat_hitting != "Select statistic" and selected_x_stat_pitching != "Select statistic") or \
            (selected_y_stat_hitting != "Select statistic" and selected_y_stat_pitching != "Select statistic"):
        messagebox.showwarning("Invalid Selection", "Please select one hitting stat and one pitching stat.")
        return

    plot_stat(selected_x_stat_hitting, selected_x_stat_pitching, selected_y_stat_hitting, selected_y_stat_pitching)


# Function to clear all selections and reset the plot
def clear_selections():
    dropdown_x_hitting.set("Select statistic")
    dropdown_x_pitching.set("Select statistic")
    dropdown_y_hitting.set("Select statistic")
    dropdown_y_pitching.set("Select statistic")

    ax.clear()
    ax.set_title("MLB Stats Visualizer", fontsize=18, fontweight="bold", color="#333")
    ax.set_xlabel("X Axis", fontsize=13, color="#555")
    ax.set_ylabel("Y Axis", fontsize=13, color="#555")
    fig.canvas.draw()


# Tkinter GUI setup
root = tk.Tk()
root.title("MLB Inspired Baseball Stats Visualizer")
root.configure(bg="#f4f4f8")


# Function to create a dropdown widget for selecting stats
def create_dropdown(frame, label_text, options):
    label = tk.Label(frame, text=label_text, font=("Helvetica", 12, "bold"), bg="#e0e4e8", fg="#333")
    label.pack(pady=5)

    dropdown = ttk.Combobox(frame, values=options, width=35, font=("Helvetica", 10), state="readonly")
    dropdown.set("Select statistic")
    dropdown.pack(pady=5)

    return dropdown


# Y-Axis Controls
y_control_frame = tk.Frame(root, padx=15, pady=15, bg="#e0e4e8", relief="groove", borderwidth=2)
y_control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=20)
tk.Label(y_control_frame, text="Y-Axis Stats", font=("Helvetica", 14, "bold"), bg="#e0e4e8", fg="#333").pack(pady=10)
dropdown_y_hitting = create_dropdown(y_control_frame, "Hitting", hitting_stats)
dropdown_y_pitching = create_dropdown(y_control_frame, "Pitching", pitching_stats)

# X-Axis Controls
x_control_frame = tk.Frame(root, padx=15, pady=15, bg="#e0e4e8", relief="groove", borderwidth=2)
x_control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=20)
tk.Label(x_control_frame, text="X-Axis Stats", font=("Helvetica", 14, "bold"), bg="#e0e4e8", fg="#333").pack(pady=10)
dropdown_x_hitting = create_dropdown(x_control_frame, "Hitting", hitting_stats)
dropdown_x_pitching = create_dropdown(x_control_frame, "Pitching", pitching_stats)

# Plot button
button = tk.Button(root, text="Generate Plot", command=plot_button_click, padx=10, pady=5,
                   font=("Helvetica", 10, "bold"), bg="#2ecc71", fg="white", relief="raised")
button.pack(pady=20)

# Clear selections button
clear_button = tk.Button(root, text="Clear Selections", command=clear_selections, padx=10, pady=5,
                         font=("Helvetica", 10, "bold"), bg="#e74c3c", fg="white", relief="raised")
clear_button.pack(pady=20)

# Embed the Matplotlib figure in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

root.mainloop()
