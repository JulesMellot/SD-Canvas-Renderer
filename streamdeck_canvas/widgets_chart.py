"""
Widgets de visualisation de données et graphiques
"""

from typing import List, Optional
import math
from .widgets import Widget
from .canvas import StreamDeckCanvas
from .utils import interpolate_color, clamp
from .validators import validate_color, validate_type, safe_clamp

class RadialGauge(Widget):
    """
    Jauge circulaire (type compteur de vitesse)
    Affiche une valeur sur un arc de cercle
    """
    def __init__(
        self, col: int, row: int, 
        value: float = 0.0,
        min_val: float = 0.0, max_val: float = 100.0,
        color: str = '#FF6B35', bg_color: str = '#4A4543',
        label: str = ""
    ):
        super().__init__(col, row, 1, 1)
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.color = color
        self.bg_color = bg_color
        self.label = label

    def set_value(self, value: float):
        self.value = safe_clamp(float(value), self.min_val, self.max_val)

    def render(self, canvas: StreamDeckCanvas):
        if not self.visible: return
        self.validate_bounds(canvas)
        
        # Configuration de l'arc
        start_angle = 135
        end_angle = 405 # 135 + 270 degres de couverture
        radius = int(canvas.button_size / 2) - 8
        
        # Calcul pourcentage
        pct = (self.value - self.min_val) / (self.max_val - self.min_val)
        current_angle = start_angle + int(pct * (end_angle - start_angle))
        
        # Fond de jauge
        canvas.draw_arc(
            self.col, self.row, radius, 
            start_angle, end_angle, 
            color=self.bg_color, width=6
        )
        
        # Valeur active
        canvas.draw_arc(
            self.col, self.row, radius, 
            start_angle, current_angle, 
            color=self.color, width=6
        )
        
        # Texte au centre
        canvas.draw_text(
            self.col, self.row, 
            text=f"{int(self.value)}", 
            size='title', color='#FFFFFF',
            offset_y=-2
        )
        
        # Label en bas
        if self.label:
            canvas.draw_text(
                self.col, self.row,
                text=self.label,
                size='tiny', color='#AAAAAA',
                align='bottom', offset_y=-5
            )


class LineGraph(Widget):
    """
    Graphique linéaire simple (Sparkline)
    """
    def __init__(
        self, col: int, row: int, width: int, height: int = 1,
        line_color: str = '#00FF00', bg_color: str = '#000000',
        max_points: int = 50
    ):
        super().__init__(col, row, width, height)
        self.data: List[float] = []
        self.max_points = max_points
        self.line_color = line_color
        self.bg_color = bg_color
        self.auto_scale = True
        self.min_y = 0.0
        self.max_y = 100.0

    def add_value(self, value: float):
        self.data.append(float(value))
        if len(self.data) > self.max_points:
            self.data.pop(0)

    def render(self, canvas: StreamDeckCanvas):
        if not self.visible: return
        self.validate_bounds(canvas)
        
        x, y, w, h = canvas.get_region_rect(self.col, self.row, self.width, self.height)
        
        # Fond
        canvas.draw.rectangle([x, y, x+w, y+h], fill=canvas.hex_to_rgb(self.bg_color))
        
        if len(self.data) < 2:
            return

        # Scaling
        curr_min = min(self.data) if self.auto_scale else self.min_y
        curr_max = max(self.data) if self.auto_scale else self.max_y
        
        if curr_max == curr_min:
            curr_max += 1
            
        # Dessin de la ligne
        points = []
        step_x = w / (len(self.data) - 1)
        
        for i, val in enumerate(self.data):
            px = x + int(i * step_x)
            # Normaliser Y (inversé car Y vers le bas)
            norm_val = (val - curr_min) / (curr_max - curr_min)
            py = y + h - int(norm_val * (h - 10)) - 5 # Padding 5px
            points.append((px, py))
            
        canvas.draw.line(points, fill=canvas.hex_to_rgb(self.line_color), width=2)


class PieChart(Widget):
    """
    Graphique en camembert simple
    """
    def __init__(
        self, col: int, row: int, 
        values: List[float], colors: List[str],
        bg_color: str = '#000000'
    ):
        super().__init__(col, row, 1, 1)
        self.values = values
        self.colors = colors
        self.bg_color = bg_color

    def update_data(self, values: List[float]):
        self.values = values

    def render(self, canvas: StreamDeckCanvas):
        if not self.visible: return
        
        total = sum(self.values)
        if total == 0: return
        
        current_angle = -90 # Commencer à 12h
        radius = int(canvas.button_size / 2) - 5
        
        for i, val in enumerate(self.values):
            sweep = (val / total) * 360
            color = self.colors[i % len(self.colors)]
            
            canvas.draw_pieslice(
                self.col, self.row, radius,
                start_angle=current_angle,
                end_angle=current_angle + sweep,
                color=color
            )
            current_angle += sweep
