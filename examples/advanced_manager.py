#!/usr/bin/env python3
"""
Stream Deck Canvas Renderer - Advanced Manager Usage
Exemple avancé montrant comment utiliser StreamDeckManager pour des cas complexes
"""

from streamdeck_canvas import StreamDeckManager, ColorPalette
from streamdeck_canvas.widgets import Button, WidgetManager
import time


def main():
    """Exemple avancé avec StreamDeckManager"""

    print("🎛️  Stream Deck Canvas Renderer - Advanced Manager")
    print("=" * 60)

    # 1. Créer le gestionnaire
    manager = StreamDeckManager()

    # 2. Scanner et afficher les appareils
    print("📱 Scan complet des appareils...")
    devices = manager.detect_devices()

    if not devices:
        print("❌ Aucun appareil disponible")
        return

    # 3. Afficher les informations détaillées
    manager.print_devices_info()

    # 4. Tenter de se connecter au premier appareil
    print("\n🔌 Tentative de connexion au premier appareil...")
    device = manager.connect_first_device(reset_deck=True)

    if not device:
        print("❌ Impossible de se connecter")
        return

    try:
        # 5. Créer un renderer pour cet appareil
        renderer = manager.create_renderer(device, debug_mode=False)
        if not renderer:
            print("❌ Impossible de créer le renderer")
            return

        canvas = renderer.canvas
        widgets = WidgetManager()

        print(f"✅ Renderer créé: {canvas.width}×{canvas.height} pixels")

        # 6. Interface de démonstration des capacités
        create_advanced_interface(widgets, device)

        # 7. Animation simple
        animate_interface(renderer, widgets, duration=10)

    finally:
        # 8. Nettoyage propre
        print("\n🧹 Nettoyage...")
        manager.close_device(device)


def create_advanced_interface(widgets, device):
    """Crée une interface avancée en fonction des capacités de l'appareil"""

    cols, rows = device['cols'], device['rows']
    canvas_size = device['canvas_size']

    print(f"🎨 Création d'une interface pour {cols}×{rows} ({canvas_size[0]}×{canvas_size[1]}px)")

    # Ligne du haut: Contrôles principaux
    widgets.add(Button(0, 0, "🏠", "HOME", bg_color=ColorPalette.PRIMARY))
    widgets.add(Button(1, 0, "⚙️", "CONFIG", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(2, 0, "📊", "MONITOR", bg_color=ColorPalette.INFO))

    # Ligne du milieu: Informations sur l'appareil
    model_name = device['deck_type'].replace(' ', '\n')
    widgets.add(Button(0, 1, "📱", model_name, bg_color=ColorPalette.BACKGROUND))

    # Afficher la grille
    grid_text = f"{cols}×{rows}"
    widgets.add(Button(1, 1, "📐", grid_text, bg_color=ColorPalette.BACKGROUND))

    # Afficher la résolution
    size_text = f"{device['button_size']}px"
    widgets.add(Button(2, 1, "🔲", size_text, bg_color=ColorPalette.BACKGROUND))

    # Ligne du bas: Statuts et actions
    widgets.add(Button(0, 2, "✅", "READY", bg_color=ColorPalette.SUCCESS))
    widgets.add(Button(1, 2, "🔄", "REFRESH", bg_color=ColorPalette.WARNING))
    widgets.add(Button(2, 2, "❌", "CLOSE", bg_color=ColorPalette.ERROR))

    # Si XL (8×4), ajouter plus d'éléments
    if cols >= 8:
        widgets.add(Button(3, 0, "🎵", "MUSIC", bg_color=ColorPalette.SUCCESS))
        widgets.add(Button(4, 0, "🌐", "WEB", bg_color=ColorPalette.INFO))
        widgets.add(Button(5, 0, "📧", "EMAIL", bg_color=ColorPalette.PRIMARY))
        widgets.add(Button(6, 0, "📅", "CAL", bg_color=ColorPalette.SURFACE))
        widgets.add(Button(7, 0, "⏰", "TIMER", bg_color=ColorPalette.WARNING))

        # Deuxième rangée étendue
        widgets.add(Button(3, 1, "💾", "SAVE", bg_color=ColorPalette.BACKGROUND))
        widgets.add(Button(4, 1, "📤", "EXPORT", bg_color=ColorPalette.BACKGROUND))
        widgets.add(Button(5, 1, "🔄", "SYNC", bg_color=ColorPalette.BACKGROUND))
        widgets.add(Button(6, 1, "🔒", "LOCK", bg_color=ColorPalette.BACKGROUND))
        widgets.add(Button(7, 1, "🌟", "STAR", bg_color=ColorPalette.BACKGROUND))

        # Troisième rangée étendue
        widgets.add(Button(3, 2, "📈", "STATS", bg_color=ColorPalette.INFO))
        widgets.add(Button(4, 2, "🔔", "ALERT", bg_color=ColorPalette.WARNING))
        widgets.add(Button(5, 2, "🎯", "TARGET", bg_color=ColorPalette.SUCCESS))
        widgets.add(Button(6, 2, "💡", "IDEA", bg_color=ColorPalette.PRIMARY))
        widgets.add(Button(7, 2, "✨", "MAGIC", bg_color=ColorPalette.ACCENT))

    # Si 4 rangées (XL)
    if rows >= 4:
        widgets.add(Button(0, 3, "🎬", "REC", bg_color=ColorPalette.ERROR))
        widgets.add(Button(1, 3, "▶️", "PLAY", bg_color=ColorPalette.SUCCESS))
        widgets.add(Button(2, 3, "⏸️", "PAUSE", bg_color=ColorPalette.PRIMARY))

        if cols >= 8:
            widgets.add(Button(3, 3, "⏹️", "STOP", bg_color=ColorPalette.SURFACE))
            widgets.add(Button(4, 3, "⏮️", "PREV", bg_color=ColorPalette.SURFACE))
            widgets.add(Button(5, 3, "⏭️", "NEXT", bg_color=ColorPalette.SURFACE))
            widgets.add(Button(6, 3, "🔇", "MUTE", bg_color=ColorPalette.WARNING))
            widgets.add(Button(7, 3, "🔊", "VOL", bg_color=ColorPalette.INFO))

    print(f"   ✅ Interface créée avec {len(widgets.widgets)} widgets")


def animate_interface(renderer, widgets, duration=10):
    """Anime l'interface pendant une durée donnée"""

    print(f"🎬 Animation de l'interface pendant {duration} secondes...")
    start_time = time.time()
    frame_count = 0

    try:
        while time.time() - start_time < duration:
            frame_start = time.time()

            # Animation simple: clignotement du bouton READY
            if frame_count % 30 < 15:
                # Trouver le bouton READY
                for widget in widgets.widgets:
                    if hasattr(widget, 'label') and widget.label == "READY":
                        widget.bg_color = ColorPalette.SUCCESS
                        break
            else:
                for widget in widgets.widgets:
                    if hasattr(widget, 'label') and widget.label == "READY":
                        widget.bg_color = ColorPalette.BACKGROUND
                        break

            # Rendu
            renderer.canvas.clear(ColorPalette.BACKGROUND)
            widgets.render_all(renderer.canvas)
            renderer.update()

            # FPS timing
            frame_duration = time.time() - frame_start
            sleep_time = max(0, (1/15) - frame_duration)
            if sleep_time > 0:
                time.sleep(sleep_time)

            frame_count += 1

    except KeyboardInterrupt:
        print("\n⏹️  Animation interrompue")

    print(f"✅ Animation terminée: {frame_count} frames rendues")


if __name__ == "__main__":
    main()