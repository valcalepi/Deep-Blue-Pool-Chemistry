from tkinter import Canvas

COLORS = {
    "deep_blue": "#003B73",
    "aqua": "#47E6B1",
    "warning": "#FFD700",
    "critical": "#FF6347",
    "safe": "#47E6B1",
    "text_primary": "#FFFFFF",
    "tile_glow": "#00FFFF",
    "hover_bg": "#005A9C",
    "dark_bg": "#1E1E1E",
    "light_bg": "#F0F0F0"
}

FONTS = {
    "title": ("Segoe UI", 18, "bold"),
    "body": ("Segoe UI", 11),
    "value": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9)
}

SPACING = {
    "pad_x": 10,
    "pad_y": 8,
    "section_gap": 12
}

def draw_gradient(canvas, width, height, color1, color2):
    """Draws a horizontal gradient background on a canvas."""
    gradient = canvas.create_rectangle(0, 0, width, height, fill=color1)
    canvas.lower(gradient)
