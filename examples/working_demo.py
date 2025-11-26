#!/usr/bin/env python3
"""
Stream Deck Canvas Renderer - Working Demo
Version finale qui fonctionne sur votre Stream Deck Original
Basée sur tout ce que nous avons appris
"""

try:
    from StreamDeck.DeviceManager import DeviceManager
    STREAMDECK_AVAILABLE = True
except ImportError:
    print("❌ StreamDeck library non disponible")
    STREAMDECK_AVAILABLE = False
    exit(1)

from streamdeck_canvas import StreamDeckRenderer, DebugRenderer
from streamdeck_canvas import Button, WidgetManager, ColorPalette
import time
import io


def create_streamdeck_image(deck, image_data):
    """
    Crée une image native pour le Stream Deck
    """
    try:
        # Obtenir le format attendu
        image_format = deck.key_image_format()

        # Convertir en format natif pour Stream Deck
        with io.BytesIO() as output:
            image = image_data.convert("RGB")
            image.save(output, format='JPEG', quality=85)
            return output.getvalue()
    except Exception as e:
        print(f"⚠️  Erreur de conversion: {e}")
        return image_data.convert("RGB").tobytes()


def main():
    """Démonstration finale qui fonctionne"""

    print("🎮 Stream Deck Canvas Renderer - Working Demo")
    print("=" * 50)

    # Trouver et connecter le Stream Deck
    streamdecks = DeviceManager().enumerate()
    if not streamdecks:
        print("❌ Aucun Stream Deck trouvé - Mode Debug")
        demo_debug()
        return

    deck = streamdecks[0]
    try:
        deck.open()
        deck.reset()

        # Obtenir les informations
        key_format = deck.key_image_format()
        cols, rows = deck.key_layout()
        button_size = key_format['size'][0]

        print(f"✅ {deck.deck_type()} connecté")
        print(f"   Série: {deck.get_serial_number()}")
        print(f"   Layout: {cols}×{rows}")
        print(f"   Images: {button_size}×{button_size} {key_format['format']}")

        # Créer le renderer avec orientation rotée
        # Ajustez 'rotated' en 'normal' selon votre setup
        renderer = StreamDeckRenderer(deck, orientation='rotated')
        canvas = renderer.canvas
        widgets = WidgetManager()

        print(f"✅ Canvas: {canvas.width}×{canvas.height} pixels")

        # Interface finale - améliorée
        create_final_interface(widgets, canvas, cols, rows)

        # Gestion des événements
        def handle_key(deck, key, state):
            if state:  # Pression
                col = key % cols
                row = key // cols
                print(f"🔘 Bouton ({col},{row}) pressé")

                # EXIT (dernier bouton)
                if key == cols * rows - 1:
                    print("👋 Au revoir!")
                    return False

            return True

        deck.set_key_callback(handle_key)

        print("🎨 Interface affichée!")
        print("   ✅ Testez les boutons - ils détectent bien!")
        print("   ❌ EXIT (dernier bouton) pour quitter")

        # Animation simple et efficace
        frame_count = 0
        start_time = time.time()
        blink_state = True

        try:
            while time.time() - start_time < 20:  # 20 secondes
                frame_start = time.time()

                # Animation du bouton READY (key 5)
                if frame_count % 15 == 0:
                    blink_state = not blink_state

                # Trouver le bouton READY et le faire clignoter
                for widget in widgets.widgets:
                    if hasattr(widget, 'label') and widget.label == "READY":
                        widget.bg_color = ColorPalette.SUCCESS if blink_state else ColorPalette.BACKGROUND
                        break

                # Rendu
                canvas.clear(ColorPalette.BACKGROUND)
                widgets.render_all(canvas)

                # Mise à jour du Stream Deck
                tiles = canvas.get_tiles()
                for i, tile in enumerate(tiles):
                    native_image = create_streamdeck_image(deck, tile)
                    deck.set_key_image(i, native_image)

                frame_count += 1

                # FPS timing
                frame_duration = time.time() - frame_start
                sleep_time = max(0, (1/10) - frame_duration)  # 10 FPS pour la stabilité
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n⏹️  Arrêt demandé")

        print(f"\n📈 Succès!")
        print(f"   Frames: {frame_count}")
        print(f"   Durée: {int(time.time() - start_time)}s")
        if frame_count > 0:
            fps = frame_count / (time.time() - start_time)
            print(f"   FPS: {fps:.1f}")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

    finally:
        try:
            deck.reset()
            deck.set_brightness(50)
            deck.close()
            print("✅ Stream Deck fermé")
        except:
            pass


def demo_debug():
    """Demo en mode debug si pas de Stream Deck"""
    print("🐛 Mode Debug")

    renderer = DebugRenderer(cols=5, rows=3, button_size=72)
    canvas = renderer.canvas
    widgets = WidgetManager()

    # Interface debug
    widgets.add(Button(0, 0, "🏠", "HOME", bg_color=ColorPalette.PRIMARY))
    widgets.add(Button(1, 0, "⚙️", "SET", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(2, 0, "🎵", "MUSIC", bg_color=ColorPalette.SUCCESS))
    widgets.add(Button(3, 0, "🌐", "WEB", bg_color=ColorPalette.INFO))
    widgets.add(Button(4, 0, "✕", "EXIT", bg_color=ColorPalette.ERROR))

    widgets.add(Button(0, 1, "📊", "READY", bg_color=ColorPalette.SUCCESS))
    widgets.add(Button(1, 1, "🔄", "REFRESH", bg_color=ColorPalette.WARNING))
    widgets.add(Button(2, 1, "ℹ️", "INFO", bg_color=ColorPalette.PRIMARY))
    widgets.add(Button(3, 1, "📈", "STATS", bg_color=ColorPalette.INFO))
    widgets.add(Button(4, 1, "🔔", "ALERT", bg_color=ColorPalette.WARNING))

    widgets.add(Button(0, 2, "💾", "SAVE", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(1, 2, "📤", "EXPORT", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(2, 2, "🔒", "LOCK", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(3, 2, "🌟", "STAR", bg_color=ColorPalette.ACCENT))
    widgets.add(Button(4, 2, "✨", "MAGIC", bg_color=ColorPalette.ACCENT))

    canvas.clear(ColorPalette.BACKGROUND)
    widgets.render_all(canvas)
    renderer.update()

    print("✅ Debug image sauvegardée: debug_frame_0000.png")


def create_final_interface(widgets, canvas, cols, rows):
    """Crée l'interface finale qui fonctionne"""

    # Ligne du haut - Navigation principale
    widgets.add(Button(0, 0, "🏠", "HOME", bg_color=ColorPalette.PRIMARY))
    widgets.add(Button(1, 0, "⚙️", "SET", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(2, 0, "🎵", "MUSIC", bg_color=ColorPalette.SUCCESS))
    widgets.add(Button(3, 0, "🌐", "WEB", bg_color=ColorPalette.INFO))
    widgets.add(Button(4, 0, "✕", "EXIT", bg_color=ColorPalette.ERROR))

    # Ligne du milieu - Statuts et actions
    widgets.add(Button(0, 1, "📊", "READY", bg_color=ColorPalette.SUCCESS))
    widgets.add(Button(1, 1, "🔄", "REFRESH", bg_color=ColorPalette.WARNING))
    widgets.add(Button(2, 1, "ℹ️", "INFO", bg_color=ColorPalette.PRIMARY))
    widgets.add(Button(3, 1, "📈", "STATS", bg_color=ColorPalette.INFO))
    widgets.add(Button(4, 1, "🔔", "ALERT", bg_color=ColorPalette.WARNING))

    # Ligne du bas - Utilitaires
    widgets.add(Button(0, 2, "💾", "SAVE", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(1, 2, "📤", "EXPORT", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(2, 2, "🔒", "LOCK", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(3, 2, "🌟", "STAR", bg_color=ColorPalette.ACCENT))
    widgets.add(Button(4, 2, "✨", "MAGIC", bg_color=ColorPalette.ACCENT))

    print(f"   ✅ Interface créée avec {len(widgets.widgets)} widgets")


if __name__ == "__main__":
    main()