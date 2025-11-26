#!/usr/bin/env python3
"""
Stream Deck Canvas Renderer - Appareil Réel
Exemple d'utilisation avec un vrai Stream Deck connecté
"""

import time
import math
from streamdeck_canvas import StreamDeckRenderer
from streamdeck_canvas.widgets import (
    Button, ProgressBar, Waveform, VUMeter, WidgetManager
)
from streamdeck_canvas.utils import ColorPalette, FPSCounter

# Import de la librairie StreamDeck officielle
try:
    from StreamDeck.DeviceManager import DeviceManager
    STREAMDECK_AVAILABLE = True
except ImportError:
    print("❌ Librairie StreamDeck non trouvée. Installez avec:")
    print("   pip install StreamDeck")
    STREAMDECK_AVAILABLE = False
    exit(1)


def find_deck():
    """Trouve le premier Stream Deck disponible"""
    streamdecks = DeviceManager().enumerate()

    if not streamdecks:
        print("❌ Aucun Stream Deck trouvé!")
        print("   Vérifiez que votre appareil est connecté et que vous avez les permissions.")
        return None

    print(f"✅ {len(streamdecks)} Stream Deck(s) trouvé(s)")

    deck = streamdecks[0]
    deck.open()
    deck.reset()

    # Afficher les informations
    key_image_format = deck.key_image_format()
    print(f"📱 Modèle: {deck.deck_type()}")
    print(f"🔢 Numéro de série: {deck.get_serial_number()}")
    print(f"🔧 Firmware: {deck.get_firmware_version()}")
    print(f"⌨️  Layout: {deck.key_layout()[0]}×{deck.key_layout()[1]} ({deck.key_count()} touches)")
    print(f"🖼️  Taille des images: {key_image_format['size'][0]}×{key_image_format['size'][1]} pixels")

    return deck


def main():
    """Démonstration avec un vrai Stream Deck"""

    if not STREAMDECK_AVAILABLE:
        print("❌ StreamDeck library non disponible")
        return

    # Trouver et ouvrir le Stream Deck
    deck = find_deck()
    if not deck:
        return

    try:
        # Créer le renderer pour l'appareil réel
        renderer = StreamDeckRenderer(deck)
        canvas = renderer.canvas
        widgets = WidgetManager()

        print("🎨 Stream Deck Canvas Renderer - Mode Appareil Réel")
        print("   Contrôles: HOME, SETTINGS, MUSIQUE, VOLUME, BRIGHTNESS")

        # === Layout pour l'appareil réel ===

        # Première rangée: Navigation principale
        home_btn = widgets.add(Button(0, 0, "🏠", "HOME",
                                    bg_color=ColorPalette.PRIMARY))

        settings_btn = widgets.add(Button(1, 0, "⚙️", "SET",
                                        bg_color=ColorPalette.SURFACE))

        music_btn = widgets.add(Button(2, 0, "🎵", "MUSIC",
                                     bg_color=ColorPalette.SUCCESS))

        # Volume slider (remplace un bouton)
        volume_slider = widgets.add(VUMeter(3, 0, height=1, level=0.5,
                                         bg_color=ColorPalette.BACKGROUND))

        brightness_btn = widgets.add(Button(4, 0, "💡", "BRIGHT",
                                         bg_color=ColorPalette.WARNING))

        # Deuxième rangée: Contrôles multimédia
        prev_btn = widgets.add(Button(0, 1, "⏮️", "PREV",
                                    bg_color=ColorPalette.SURFACE))

        play_btn = widgets.add(Button(1, 1, "⏸️", "PAUSE",
                                    bg_color=ColorPalette.PRIMARY))

        next_btn = widgets.add(Button(2, 1, "⏭️", "NEXT",
                                    bg_color=ColorPalette.SURFACE))

        # Visualisation audio sur 2 boutons
        waveform = widgets.add(Waveform(3, 1, width=2, progress=0.0,
                                       bg_color=ColorPalette.BACKGROUND))

        # Troisième rangée: Informations et statuts
        cpu_usage = widgets.add(Button(0, 2, "CPU", "45%",
                                    bg_color=ColorPalette.INFO))

        memory_usage = widgets.add(Button(1, 2, "MEM", "67%",
                                       bg_color=ColorPalette.WARNING))

        network_btn = widgets.add(Button(2, 2, "🌐", "NET",
                                      bg_color=ColorPalette.SUCCESS))

        clock_btn = widgets.add(Button(3, 2, "🕐", "12:34",
                                    bg_color=ColorPalette.BACKGROUND))

        exit_btn = widgets.add(Button(4, 2, "✕", "EXIT",
                               bg_color=ColorPalette.ERROR))

        # Gestionnaire d'événements
        def handle_button_press(col, row, key):
            """Gère les pressions de boutons"""
            print(f"🔘 Bouton pressé: ({col}, {row}) - key {key}")

            # Effets visuels
            if col == 0 and row == 0:  # HOME
                home_btn.pressed = True
                print("   → Retour à l'accueil")
            elif col == 1 and row == 0:  # SETTINGS
                settings_btn.pressed = True
                print("   → Ouverture des paramètres")
            elif col == 2 and row == 0:  # MUSIC
                music_btn.pressed = True
                print("   → Lecteur de musique")
            elif col == 4 and row == 0:  # BRIGHTNESS
                current_brightness = deck.get_brightness()
                new_brightness = 30 if current_brightness > 50 else 80
                deck.set_brightness(new_brightness)
                brightness_btn.label = f"{new_brightness}%"
                print(f"   → Luminosité: {new_brightness}%")
            elif col == 1 and row == 1:  # PLAY/PAUSE
                if play_btn.icon == "▶️":
                    play_btn.icon = "⏸️"
                    play_btn.label = "PAUSE"
                    play_btn.bg_color = ColorPalette.PRIMARY
                    print("   → Lecture en pause")
                else:
                    play_btn.icon = "▶️"
                    play_btn.label = "PLAY"
                    play_btn.bg_color = ColorPalette.SUCCESS
                    print("   → Lecture démarrée")
            elif col == 4 and row == 2:  # EXIT
                print("   → Arrêt demandé")
                return False  # Arrêter la boucle

            return True  # Continuer

        # Configurer le callback
        renderer.on_button_press = handle_button_press

        # Variables d'animation
        start_time = time.time()
        frame_count = 0
        fps_counter = FPSCounter()

        print("\n🎮 Interface active! Utilisez les boutons du Stream Deck.")
        print("   Pressez EXIT (bouton en bas à droite) pour quitter.")
        print("   Pressez Ctrl+C dans le terminal pour arrêter.\n")

        # Boucle de rendu principale
        running = True
        while running:
            frame_start = time.time()
            elapsed = time.time() - start_time

            # Animation du waveform
            waveform_progress = (math.sin(elapsed * 0.3) + 1) / 2
            waveform.set_progress(waveform_progress)

            # Animation du volume (simulation)
            volume_level = 0.3 + 0.2 * math.sin(elapsed * 0.5)
            volume_slider.set_level(volume_level)

            # Animation des statuts système
            if frame_count % 30 == 0:  # Toutes les 2 secondes
                cpu_percent = 40 + int(20 * math.sin(elapsed * 0.2))
                mem_percent = 60 + int(15 * math.sin(elapsed * 0.15))

                cpu_usage.label = f"{cpu_percent}%"
                memory_usage.label = f"{mem_percent}%"

                # Changer la couleur selon le niveau
                cpu_usage.bg_color = (ColorPalette.ERROR if cpu_percent > 70 else
                                     ColorPalette.WARNING if cpu_percent > 50 else
                                     ColorPalette.SUCCESS)
                memory_usage.bg_color = (ColorPalette.ERROR if mem_percent > 80 else
                                        ColorPalette.WARNING if mem_percent > 60 else
                                        ColorPalette.SUCCESS)

            # Mise à jour de l'horloge
            current_time = time.strftime("%H:%M")
            clock_btn.label = current_time

            # Remise à zéro des états pressed
            if frame_count % 10 == 0:
                home_btn.pressed = False
                settings_btn.pressed = False
                music_btn.pressed = False

            # Effacer et rendre
            canvas.clear(ColorPalette.BACKGROUND)
            widgets.render_all(canvas)

            # Mettre à jour le Stream Deck
            renderer.update()

            # FPS et stats
            current_fps = fps_counter.update()
            if frame_count % 60 == 0:  # Toutes les 4 secondes
                print(f"📊 FPS: {current_fps:.1f} | Frame: {frame_count} | Runtime: {int(elapsed)}s")

            # Timing pour 15 FPS
            frame_duration = time.time() - frame_start
            sleep_time = max(0, (1/15) - frame_duration)
            if sleep_time > 0:
                time.sleep(sleep_time)

            frame_count += 1

    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé via Ctrl+C")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        # Nettoyage
        print("🧹 Nettoyage en cours...")
        try:
            deck.reset()
            deck.set_brightness(50)
            deck.close()
            print("✅ Stream Deck fermé proprement")
        except:
            print("⚠️  Erreur lors de la fermeture du Stream Deck")

        print(f"📈 Statistiques finales:")
        print(f"   Frames rendues: {frame_count}")
        print(f"   FPS moyen: {fps_counter.get_fps():.1f}")
        print(f"   Durée totale: {int(time.time() - start_time)}s")


if __name__ == "__main__":
    main()