import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.animation import FuncAnimation
import folium
from tkinter import filedialog
from geopy.distance import great_circle
from datetime import datetime

class PolarPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Polar Coordinate Plotter")
        
        # Make the window full-screen
        self.root.attributes('-fullscreen', True)
        
        # Top frame for the title
        self.top_frame = tk.Frame(root, bg='#333333')
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.title_label = ttk.Label(self.top_frame, text="Polar Coordinate Plotter", font=("Helvetica", 24, "bold"), foreground="white", background="#333333")
        self.title_label.pack(padx=10, pady=10)

        # Sidebar for controls
        self.sidebar_frame = tk.Frame(root, bg='#444444', width=300)
        self.sidebar_frame.grid(row=1, column=0, sticky="ns")
        
        # Input for radius and angle
        self.radius_label = ttk.Label(self.sidebar_frame, text="Radius (r):", font=("Helvetica", 14), background="#444444", foreground="white")
        self.radius_label.pack(padx=10, pady=(20, 5))
        self.radius_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 14))
        self.radius_entry.pack(padx=10, pady=5)
        
        self.theta_label = ttk.Label(self.sidebar_frame, text="Angle (θ in degrees):", font=("Helvetica", 14), background="#444444", foreground="white")
        self.theta_label.pack(padx=10, pady=5)
        self.theta_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 14))
        self.theta_entry.pack(padx=10, pady=5)
        
        # Input for current location
        self.lat_label = ttk.Label(self.sidebar_frame, text="Current Latitude:", font=("Helvetica", 14), background="#444444", foreground="white")
        self.lat_label.pack(padx=10, pady=(20, 5))
        self.lat_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 14))
        self.lat_entry.pack(padx=10, pady=5)
        
        self.lon_label = ttk.Label(self.sidebar_frame, text="Current Longitude:", font=("Helvetica", 14), background="#444444", foreground="white")
        self.lon_label.pack(padx=10, pady=5)
        self.lon_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 14))
        self.lon_entry.pack(padx=10, pady=5)
        
        # Buttons
        self.add_button = ttk.Button(self.sidebar_frame, text="Add Coordinates", command=self.add_coordinates, style="TButton")
        self.add_button.pack(padx=10, pady=(20, 10))
        
        self.clear_button = ttk.Button(self.sidebar_frame, text="Clear Graph", command=self.clear_graph, style="TButton")
        self.clear_button.pack(padx=10, pady=10)
        
        self.show_map_button = ttk.Button(self.sidebar_frame, text="Show on Map", command=self.show_on_map, style="TButton")
        self.show_map_button.pack(padx=10, pady=(20, 10))

        self.error_label = ttk.Label(self.sidebar_frame, text="", font=("Helvetica", 10), foreground="red", background="#444444")
        self.error_label.pack(padx=10, pady=10)

        # Styling for buttons
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 14), padding=10)
        style.map("TButton",
                  foreground=[('pressed', 'white'), ('active', 'white')],
                  background=[('pressed', '#555555'), ('active', '#555555')])

        # Bottom content - black background (for the polar plot)
        self.bottom_frame = tk.Frame(root, bg='black')
        self.bottom_frame.grid(row=1, column=1, sticky="nsew")
        
        # Set up the matplotlib figure and axis with a black theme
        self.figure, self.ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        self._initialize_plot()
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.bottom_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize points list
        self.points = []
        
        # Animation settings
        self.animation_interval = 50  # Faster animation
        self.animation_max_radius = 10  # Ensure it reaches the outer edge
        self.animation_line = None
        self.animation = FuncAnimation(self.figure, self.animate, frames=np.linspace(0, self.animation_max_radius, 100), interval=self.animation_interval, blit=True)
        
        # Make the graph larger and responsive to screen size
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def _initialize_plot(self):
        """Initializes or resets the polar plot with default settings."""
        self.figure.patch.set_facecolor('black')  # Set figure background color
        self.ax.set_facecolor('black')  # Set axis background color
        self.ax.tick_params(colors='white')  # Set tick color to white
        self.ax.xaxis.label.set_color('white')  # Set x-axis label color to white
        self.ax.yaxis.label.set_color('white')  # Set y-axis label color to white
        self.ax.spines['polar'].set_color('white')  # Set polar spine color to white
        self.ax.set_ylim(0, 10)  # Increase initial radius to accommodate the beam
        self.ax.grid(True, color='white')  # Set grid color to white
        self.ax.plot([0], [0], 'go')  # Green dot at the origin
    
    def add_coordinates(self):
        try:
            # Clear any previous error message
            self.error_label.config(text="")
            
            # Get user input
            r = float(self.radius_entry.get())
            theta_deg = float(self.theta_entry.get())
            theta_rad = np.deg2rad(theta_deg)
            
            # Store the point
            self.points.append((theta_rad, r))
            
            # Update the radius limit dynamically
            max_radius = max(r for _, r in self.points)
            self.ax.set_ylim(0, max_radius + 1)  # Add a little padding
            
            # Plot the point
            self.ax.plot([theta_rad], [r], 'ro')  # Red dot for each point
            self.canvas.draw()
        except ValueError:
            self.error_label.config(text="Please enter valid numeric values for radius and angle.")
        
    def clear_graph(self):
        # Clear the plot and reset the points
        self.points.clear()
        self.ax.clear()
        self._initialize_plot()  # Reinitialize plot settings
        self.canvas.draw()

    def animate(self, radius):
        if self.animation_line:
            self.animation_line.remove()
        
        # Draw a circle (beam) expanding from the origin
        self.animation_line, = self.ax.plot(np.linspace(0, 2 * np.pi, 100), np.full(100, radius), color='cyan', alpha=0.5)
        
        # Redraw existing points on top of the animation
        for theta_rad, r in self.points:
            self.ax.plot([theta_rad], [r], 'ro')  # Red dot for each point
        
        return self.animation_line,

    def show_on_map(self):
        try:
            # Get current location input
            current_lat = float(self.lat_entry.get())
            current_lon = float(self.lon_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for current location.")
            return
        
        # Create a folium map centered at the current location
        m = folium.Map(location=[current_lat, current_lon], zoom_start=12)

        # Add the current location marker
        folium.Marker([current_lat, current_lon], popup="Current Location", icon=folium.Icon(color='green')).add_to(m)

        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add markers for each point
        for theta_rad, r in self.points:
            # Convert polar coordinates to lat/lon for simplicity
            lat = current_lat + r * np.sin(theta_rad) * 0.01  # Adjust factor as needed
            lon = current_lon + r * np.cos(theta_rad) * 0.01  # Adjust factor as needed

            # Calculate the distance to the current location
            distance = great_circle((current_lat, current_lon), (lat, lon)).km

            # Create a popup with latitude, longitude, distance, and current time
            popup_text = (
                f"Latitude: {lat:.4f}\n"
                f"Longitude: {lon:.4f}\n"
                f"Distance: {distance:.2f} km\n"
                f"Time: {current_time}"
            )

            # Add a marker for each enemy point
            folium.Marker(
                [lat, lon],
                popup=popup_text,
                icon=folium.Icon(color='red')
            ).add_to(m)

        # Save map to an HTML file
        map_file = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
        if map_file:
            m.save(map_file)
            messagebox.showinfo("Map Saved", "Map has been saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PolarPlotter(root)
    root.mainloop()
