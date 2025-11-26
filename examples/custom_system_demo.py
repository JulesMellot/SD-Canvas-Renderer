#!/usr/bin/env python3
"""
Démonstration du système de création rapide de widgets.
Montre comment créer des composants sans boilerplate via SimpleWidget et @functional_widget.
"""

from streamdeck_canvas import StreamDeckApp, SimpleWidget, functional_widget
import math
import random

# --- Méthode 1 : Le Widget Fonctionnel (Pour des trucs simples) ---

@functional_widget(width=1, height=1)
def TrafficLight(self, canvas):
    """Un feu tricolore simple"""
    # self.state est accessible si passé en argument
    state = getattr(self, 'state', 'red')
    
    color_map = {
        'red': '#FF0000',
        'yellow': '#FFCC00',
        'green': '#00FF00'
    }
    
    # Dessiner le fond
    canvas.draw_rect(self.col, self.row, color='#333333', radius=10)
    
    # Dessiner la lumière
    active_color = color_map.get(state, '#FF0000')
    canvas.draw_circle(self.col, self.row, radius=20, color=active_color)

# --- Méthode 2 : La Classe Simplifiée (Pour des trucs avec état/animation) ---

class BouncingBall(SimpleWidget):
    def setup(self):
        self.ball_y = 0
        self.velocity = 0
        self.gravity = 9.8
        # self.color vient du constructeur automatiquement
        if not hasattr(self, 'color'): self.color = '#00FFFF'

    def on_update(self, dt):
        # Simulation physique simple
        self.velocity += self.gravity * dt * 20 # *20 pour effet visuel
        self.ball_y += self.velocity * dt * 10
        
        # Rebond au sol (72px - 10px radius)
        max_y = 72 - 20
        if self.ball_y > max_y:
            self.ball_y = max_y
            self.velocity = -self.velocity * 0.8 # Perte d'énergie

    def on_draw(self, canvas):
        # Fond
        canvas.draw_rect(self.col, self.row, color='#111111')
        
        # Balle
        x, y, w, h = canvas.get_button_rect(self.col, self.row)
        center_x = x + w // 2
        ball_draw_y = y + 10 + int(self.ball_y)
        
        canvas.draw.ellipse(
            [center_x-10, ball_draw_y-10, center_x+10, ball_draw_y+10],
            fill=canvas.hex_to_rgb(self.color)
        )

# --- Lancement de l'App ---

app = StreamDeckApp(target_fps=30, debug_cols=5, debug_rows=3)
t = 0.0

@app.on_setup
def setup(canvas, widgets):
    # Utilisation du widget fonctionnel
    widgets.add(TrafficLight(0, 0, state='red'))
    widgets.add(TrafficLight(1, 0, state='yellow'))
    widgets.add(TrafficLight(2, 0, state='green'))
    
    # Utilisation du widget simplifié
    widgets.add(BouncingBall(0, 1, color='#FF00FF'))
    widgets.add(BouncingBall(1, 1, color='#00FFFF'))
    widgets.add(BouncingBall(2, 1, color='#FFFF00'))

@app.on_loop
def loop(canvas, widgets, delta_time):
    global t
    t += delta_time
    
    # Animation du feu de circulation
    # On modifie dynamiquement les propriétés du widget fonctionnel
    light = widgets.find_widget_at(0, 0)
    if int(t) % 3 == 0: light.state = 'red'
    elif int(t) % 3 == 1: light.state = 'yellow'
    else: light.state = 'green'

if __name__ == "__main__":
    app.run()
