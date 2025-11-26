#!/usr/bin/env python3
"""
Exemple d'utilisation de StreamDeckApp
Montre comment créer une application rapidement avec la nouvelle API.
"""

from streamdeck_canvas.app import StreamDeckApp
from streamdeck_canvas.widgets import Button, ProgressBar
from streamdeck_canvas.utils import ColorPalette
import math

# Créer l'application
app = StreamDeckApp(target_fps=30, debug_cols=5, debug_rows=3)

# Variable globale pour l'animation
animation_time = 0.0

@app.on_setup
def setup(canvas, widgets):
    """Configuration initiale"""
    # Ajouter un bouton
    widgets.add(Button(0, 0, "🚀", "START", bg_color=ColorPalette.PRIMARY))
    
    # Ajouter une barre de progression
    global progress_bar
    progress_bar = widgets.add(ProgressBar(0, 1, width=5))
    
    print("✅ Setup terminé")

@app.on_loop
def loop(canvas, widgets, delta_time):
    """Boucle principale"""
    global animation_time
    animation_time += delta_time
    
    # 1. Dessiner un fond en dégradé (Nouvelle fonctionnalité !)
    # On le fait avant de rendre les widgets
    canvas.draw_gradient_rect(
        0, 0, canvas.cols, canvas.rows,
        color_start='#1A1110',
        color_end='#000000',
        direction='vertical'
    )
    
    # 2. Animation de la barre de progression
    val = (math.sin(animation_time) + 1) / 2  # 0.0 à 1.0
    progress_bar.set_progress(val)
    
    # 3. Changer la couleur du bouton selon le temps
    btn = widgets.find_widget_at(0, 0)
    if btn:
        if int(animation_time) % 2 == 0:
            btn.bg_color = ColorPalette.PRIMARY
        else:
            btn.bg_color = ColorPalette.SECONDARY

if __name__ == "__main__":
    app.run()
