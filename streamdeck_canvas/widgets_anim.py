"""
Widgets d'animation et effets visuels
"""

from .widgets import Widget
from .canvas import StreamDeckCanvas
from .utils import rgb_to_hex
import random

class MatrixRain(Widget):
    """
    Effet Matrix (pluie numérique)
    """
    def __init__(
        self, col: int, row: int, width: int, height: int,
        color: str = '#00FF00', speed: int = 1
    ):
        super().__init__(col, row, width, height)
        self.color = color
        self.drops = [] # Liste de positions Y pour chaque colonne de pixels
        self.initialized = False

    def render(self, canvas: StreamDeckCanvas):
        if not self.visible: return
        self.validate_bounds(canvas)
        
        x, y, w, h = canvas.get_region_rect(self.col, self.row, self.width, self.height)
        
        # Init drops
        num_columns = w // 8 # Espacement de 8px
        if not self.initialized or len(self.drops) != num_columns:
            self.drops = [random.randint(-h, 0) for _ in range(num_columns)]
            self.initialized = True
            
        # Fond noir (semi transparent pour trail effect?) 
        # En canvas statique on redessine tout, donc pas de trail auto facile
        # On dessine juste les drops
        canvas.draw.rectangle([x, y, x+w, y+h], fill=(0,0,0))
        
        rgb = canvas.hex_to_rgb(self.color)
        
        for i, drop_y in enumerate(self.drops):
            px = x + i * 8
            py = y + drop_y
            
            # Dessiner la "tête" brillante
            if 0 <= drop_y < h:
                canvas.draw.text((px, py), text=chr(random.randint(33, 126)), fill=(255, 255, 255), font=canvas.fonts['tiny'])
            
            # Dessiner la queue (2-3 char plus sombres)
            for j in range(1, 4):
                tail_y = py - j * 10
                if 0 <= tail_y < h:
                    darker = (0, int(255 * (1 - j/4)), 0)
                    canvas.draw.text((px, tail_y), text=chr(random.randint(33, 126)), fill=darker, font=canvas.fonts['tiny'])

            # Update position
            self.drops[i] += random.randint(2, 5)
            if self.drops[i] > h:
                self.drops[i] = random.randint(-20, 0)


class BreathingRect(Widget):
    """
    Rectangle qui pulse (effet respiration)
    """
    def __init__(
        self, col: int, row: int, 
        color: str = '#FF0000', speed: float = 0.1
    ):
        super().__init__(col, row, 1, 1)
        self.color = color
        self.speed = speed
        self.t = 0.0

    def render(self, canvas: StreamDeckCanvas):
        if not self.visible: return
        
        import math
        self.t += self.speed
        
        # Alpha varie de 50 à 255
        alpha = int(152.5 + 102.5 * math.sin(self.t))
        
        base_rgb = canvas.hex_to_rgb(self.color)
        
        # Comme PIL draw.rectangle ne gère pas alpha direct sur RGB image sans transparence,
        # on triche ou on simule en mixant avec noir
        r, g, b = base_rgb
        factor = alpha / 255.0
        curr_rgb = (int(r * factor), int(g * factor), int(b * factor))
        
        hex_color = rgb_to_hex(*curr_rgb)
        canvas.draw_rect(self.col, self.row, color=hex_color, radius=15)
