#!/usr/bin/env python3
"""
Showcase V2 - Démonstration des nouveaux composants avancés
"""

from streamdeck_canvas import StreamDeckApp, ColorPalette
from streamdeck_canvas.widgets import Button, ScrollingText, WidgetManager
from streamdeck_canvas.widgets_chart import RadialGauge, LineGraph, PieChart
from streamdeck_canvas.widgets_audio import SpectrumVisualizer, RotaryVolume
from streamdeck_canvas.widgets_anim import MatrixRain, BreathingRect

import math
import random

app = StreamDeckApp(target_fps=30, debug_cols=5, debug_rows=3)

# Global state variables
t = 0.0
audio_levels = [0.0] * 10
graph_data = [0.0] * 20

@app.on_setup
def setup(canvas, widgets):
    # 1. Charts Row (Top)
    widgets.add(RadialGauge(0, 0, label="CPU", color='#FF6B35', max_val=100))
    widgets.add(LineGraph(1, 0, width=2, line_color='#00FF00'))
    widgets.add(PieChart(3, 0, values=[30, 50, 20], colors=['#FF0000', '#00FF00', '#0000FF']))
    widgets.add(BreathingRect(4, 0, color='#FF00FF'))

    # 2. Audio Row (Middle)
    widgets.add(RotaryVolume(0, 1, level=0.5))
    widgets.add(SpectrumVisualizer(1, 1, width=3, num_bars=15))
    widgets.add(Button(4, 1, "MUTE", "", bg_color='#333333'))

    # 3. Animation Row (Bottom)
    widgets.add(MatrixRain(0, 2, width=2, height=1))
    widgets.add(ScrollingText(2, 2, width=3, text="Stream Deck Canvas - New Widgets Showcase ... "))

@app.on_loop
def loop(canvas, widgets, delta_time):
    global t
    t += delta_time

    # Update CPU Gauge (Simulated)
    cpu_val = 50 + 40 * math.sin(t)
    widgets.find_widget_at(0, 0).set_value(cpu_val)

    # Update Graph
    if int(t * 10) % 2 == 0: # Add point every few frames
        new_val = 50 + random.randint(-20, 20)
        widgets.find_widget_at(1, 0).add_value(new_val)

    # Update Pie Chart (Rotate values)
    pie = widgets.find_widget_at(3, 0)
    v1 = 30 + 10 * math.sin(t)
    v2 = 50
    v3 = 20 + 10 * math.cos(t)
    pie.update_data([v1, v2, v3])

    # Update Volume Knob
    vol = (math.sin(t * 0.5) + 1) / 2
    widgets.find_widget_at(0, 1).set_level(vol)

    # Update Spectrum
    spectrum = widgets.find_widget_at(1, 1)
    # Random bars logic
    levels = [random.random() * vol for _ in range(15)]
    spectrum.set_values(levels)

if __name__ == "__main__":
    print("Lancement de la démo V2...")
    app.run()
