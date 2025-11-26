"""
Widgets dédiés à l'audio
"""

from typing import List
import math
from .widgets import Widget
from .canvas import StreamDeckCanvas
from .validators import validate_color

class SpectrumVisualizer(Widget):
    """
    Visualiseur de spectre audio (Barres)
    """
    def __init__(
        self, col: int, row: int, width: int, height: int = 1,
        num_bars: int = 10,
        bar_color: str = '#00CCFF',
        peak_color: str = '#FFFFFF'
    ):
        super().__init__(col, row, width, height)
        self.num_bars = num_bars
        self.values = [0.0] * num_bars
        self.bar_color = bar_color
        self.peak_color = peak_color
        
    def set_values(self, values: List[float]):
        """Met à jour les valeurs (0.0 à 1.0)"""
        self.values = [float(v) for v in values[:self.num_bars]]
        # Pad if needed
        while len(self.values) < self.num_bars:
            self.values.append(0.0)

    def render(self, canvas: StreamDeckCanvas):
        if not self.visible: return
        self.validate_bounds(canvas)
        
        x, y, w, h = canvas.get_region_rect(self.col, self.row, self.width, self.height)
        
        # Fond noir
        canvas.draw.rectangle([x, y, x+w, y+h], fill=(0,0,0))
        
        bar_width = w / self.num_bars
        padding = 1
        
        rgb_bar = canvas.hex_to_rgb(self.bar_color)
        
        for i, val in enumerate(self.values):
            val = max(0.0, min(1.0, val))
            bar_h = int(val * h)
            bx = x + int(i * bar_width)
            
            if bar_h > 0:
                canvas.draw.rectangle(
                    [bx + padding, y + h - bar_h, 
                     bx + int(bar_width) - padding, y + h],
                    fill=rgb_bar
                )


class RotaryVolume(Widget):
    """
    Bouton de volume rotatif
    """
    def __init__(
        self, col: int, row: int,
        level: float = 0.5,
        active_color: str = '#FFB627',
        indicator_color: str = '#FFFFFF'
    ):
        super().__init__(col, row, 1, 1)
        self.level = level
        self.active_color = active_color
        self.indicator_color = indicator_color

    def set_level(self, level: float):
        self.level = max(0.0, min(1.0, level))

    def render(self, canvas: StreamDeckCanvas):
        if not self.visible: return
        
        # Cercle de fond
        radius = int(canvas.button_size / 2) - 10
        canvas.draw_circle(
            self.col, self.row, radius,
            color='#222222', border='#555555'
        )
        
        x, y, w, h = canvas.get_button_rect(self.col, self.row)
        cx, cy = x + w//2, y + h//2
        
        # Indicateur de rotation
        # -135 deg (min) à +135 deg (max)
        angle_range = 270
        start_deg = 135
        current_deg = start_deg + (self.level * angle_range)
        
        # Conversion deg->rad pour calcul position
        rad = math.radians(current_deg + 90) # +90 car 0 est à droite
        
        ix = cx + int((radius - 8) * math.cos(rad))
        iy = cy + int((radius - 8) * math.sin(rad))
        
        # Point indicateur
        canvas.draw.ellipse(
            [ix-4, iy-4, ix+4, iy+4],
            fill=canvas.hex_to_rgb(self.indicator_color)
        )
        
        # Arc de niveau actif autour
        canvas.draw_arc(
            self.col, self.row, radius + 5,
            start_angle=start_deg,
            end_angle=int(current_deg),
            color=self.active_color,
            width=3
        )
