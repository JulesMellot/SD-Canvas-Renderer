#!/usr/bin/env python3
"""
Stream Deck Canvas Renderer - Utilisation de Base
Exemple simple pour commencer avec le renderer
"""

from streamdeck_canvas import StreamDeckCanvas
from streamdeck_canvas.renderer import DebugRenderer
from streamdeck_canvas.widgets import Button, WidgetManager
from streamdeck_canvas.utils import ColorPalette


def main():
    """Exemple de base simple"""

    # Créer un renderer debug (pas besoin de Stream Deck physique)
    renderer = DebugRenderer(cols=5, rows=3, button_size=72)
    canvas = renderer.canvas

    # Créer un gestionnaire de widgets
    widgets = WidgetManager()

    # Ajouter quelques boutons simples
    home_btn = widgets.add(Button(0, 0, "🏠", "HOME",
                                bg_color=ColorPalette.PRIMARY))

    settings_btn = widgets.add(Button(1, 0, "⚙️", "SETTINGS",
                                    bg_color=ColorPalette.SURFACE))

    music_btn = widgets.add(Button(2, 0, "🎵", "MUSIC",
                               bg_color=ColorPalette.SUCCESS))

    # Effacer le canvas
    canvas.clear(ColorPalette.BACKGROUND)

    # Rendre tous les widgets
    widgets.render_all(canvas)

    # Mettre à jour le renderer (sauvegarde une image)
    renderer.update()

    print("✅ Exemple de base terminé!")
    print("📁 Image sauvegardée: debug_frame_0000.png")


if __name__ == "__main__":
    main()