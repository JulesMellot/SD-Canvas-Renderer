#!/usr/bin/env python3
"""
Stream Deck Canvas Renderer - Showcase Complète
Démonstration de toutes les fonctionnalités du renderer
"""

import time
import math
import random
from streamdeck_canvas import StreamDeckCanvas
from streamdeck_canvas.renderer import DebugRenderer
from streamdeck_canvas.widgets import (
    Button, ProgressBar, Waveform, VUMeter, Timer,
    ScrollingText, LoadingSpinner, Grid, WidgetManager
)
from streamdeck_canvas.utils import Timer, FPSCounter, ColorPalette


def main():
    """Demo complète qui montre toutes les capacités du système"""

    # Créer le renderer (mode debug pour développement)
    renderer = DebugRenderer(cols=5, rows=3, button_size=72)
    canvas = renderer.canvas

    # Créer le gestionnaire de widgets
    widgets = WidgetManager()

    # === Première rangée : Contrôles et navigation ===

    # Bouton HOME animé
    home_btn = widgets.add(Button(0, 0, "🏠", "HOME",
                                 bg_color=ColorPalette.PRIMARY))

    # Bouton Settings
    settings_btn = widgets.add(Button(1, 0, "⚙️", "SETTINGS",
                                    bg_color=ColorPalette.SURFACE))

    # Bouton Exit
    exit_btn = widgets.add(Button(2, 0, "✕", "EXIT",
                                bg_color=ColorPalette.ERROR))

    # Infos (remplace le timer temporairement)
    info_btn = widgets.add(Button(3, 0, "ℹ️", "INFO",
                                bg_color=ColorPalette.INFO))

    # FPS Counter (utilitaire interne)
    fps_timer = FPSCounter()

    # === Deuxième rangée : Audio et visualisation ===

    # Waveform audio avec plusieurs cues
    waveform = widgets.add(Waveform(0, 1, width=3, progress=0.0,
                                   bg_color=ColorPalette.BACKGROUND))

    # Ajouter quelques cues markers
    waveform.add_cue(0.15)
    waveform.add_cue(0.45)
    waveform.add_cue(0.75)

    # VU-mètre vertical
    vu_left = widgets.add(VUMeter(3, 1, height=1, level=0.0,
                                 bg_color=ColorPalette.BACKGROUND))

    # VU-mètre vertical stéréo
    vu_right = widgets.add(VUMeter(4, 1, height=1, level=0.0,
                                  bg_color=ColorPalette.BACKGROUND))

    # === Troisième rangée : Progression et statuts ===

    # Barre de progression multi-boutons
    progress_bar = widgets.add(ProgressBar(0, 2, width=3, progress=0.0,
                                         bg_color=ColorPalette.BACKGROUND,
                                         fill_color=ColorPalette.PRIMARY))

    # Spinner de chargement
    spinner = widgets.add(LoadingSpinner(3, 2, color=ColorPalette.ACCENT))

    # Scrolling text pour les noms longs
    scrolling = widgets.add(ScrollingText(4, 2, width=1,
                                        text="Super_Long_File_Name_With_Extension.mp3",
                                        bg_color=ColorPalette.BACKGROUND))

    # Animation state
    start_time = time.time()
    demo_timer = Timer()
    demo_timer.start()

    print("🎨 Stream Deck Canvas Renderer - Showcase Démarrée!")
    print("   Features: Navigation, Audio Viz, Progress, Scrolling Text, Animations")
    print("   Mode: Debug (sauvegarde des frames)")

    # Boucle de démonstration
    frame_count = 0
    try:
        while frame_count < 300:  # 20 secondes à 15 FPS

            frame_start = time.time()

            # Clear canvas
            canvas.clear(ColorPalette.BACKGROUND)

            # === Animations basées sur le temps ===
            elapsed = demo_timer.elapsed()

            # Animation du waveform (position dans la piste)
            waveform_progress = (math.sin(elapsed * 0.3) + 1) / 2  # 0 à 1
            waveform.set_progress(waveform_progress)

            # Animation des VU-mètres (gauche/droite différents)
            vu_left_level = (math.sin(elapsed * 2.5) + 1) / 2 * 0.8
            vu_right_level = (math.cos(elapsed * 3.0) + 1) / 2 * 0.9
            vu_left.set_level(vu_left_level)
            vu_right.set_level(vu_right_level)

            # Animation de la barre de progression
            progress = ((elapsed % 10) / 10)  # Cycle de 10 secondes
            progress_bar.set_progress(progress)

            # Animation du bouton info (clignote)
            if frame_count % 30 < 15:
                info_btn.bg_color = ColorPalette.INFO
            else:
                info_btn.bg_color = ColorPalette.SURFACE

            # === Changements périodiques ===

            # Changer le texte défilant toutes les 5 secondes
            if int(elapsed) % 5 == 0 and frame_count % 15 == 0:
                texts = [
                    "Super_Long_File_Name_With_Extension.mp3",
                    "Another_Very_Long_Track_Title_Files.wav",
                    "Podcast_Episode_42_The_Long_Journey.flac",
                    "Streaming_Session_Recording_Final_Edit.m4a"
                ]
                scrolling.set_text(random.choice(texts))

            # Effet pressed sur les boutons cycliquement
            if frame_count % 30 == 0:  # Toutes les 2 secondes
                home_btn.pressed = not home_btn.pressed
            elif frame_count % 30 == 10:
                settings_btn.pressed = not settings_btn.pressed
            elif frame_count % 30 == 20:
                exit_btn.pressed = not exit_btn.pressed

            # === Rendu de tous les widgets ===
            widgets.render_all(canvas)

            # === Informations de debug ===
            current_fps = fps_timer.update()

            # Afficher les stats toutes les 2 secondes
            if frame_count % 30 == 0:
                print(f"📊 Frame {frame_count:03d} | FPS: {current_fps:.1f} | "
                      f"Time: {format_time(elapsed)} | Progress: {progress:.0%}")

            # Mettre à jour le renderer
            renderer.update()

            # Timing pour ~15 FPS
            frame_duration = time.time() - frame_start
            sleep_time = max(0, (1/15) - frame_duration)
            if sleep_time > 0:
                time.sleep(sleep_time)

            frame_count += 1

    except KeyboardInterrupt:
        print("\n⏹️  Démonstration interrompue")

    # Animation de fin
    print("🎬 Animation de fin...")
    for i in range(15):
        canvas.clear()

        # Fade out
        alpha = 1.0 - (i / 15.0)
        fade_color = interpolate_color(ColorPalette.BACKGROUND, '#000000', i / 15.0)
        canvas.clear(fade_color)

        # Texte de fin
        canvas.draw_text(2, 1, "FIN!", color=ColorPalette.TEXT_PRIMARY, size='huge')

        renderer.update()
        time.sleep(1/15)

    print(f"✅ Démonstration terminée! {frame_count} frames rendues")
    print(f"📁 Images sauvegardées dans le dossier courant")
    print(f"⏱️  Durée totale: {format_time(demo_timer.elapsed())}")
    print(f"🚀 FPS moyen: {fps_timer.get_fps():.1f}")


def format_time(seconds: float) -> str:
    """Formate le temps en MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def interpolate_color(color1: str, color2: str, factor: float) -> str:
    """Interpole entre deux couleurs (version simple)"""
    factor = max(0.0, min(1.0, factor))

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(r, g, b):
        return f'#{r:02X}{g:02X}{b:02X}'

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * factor)
    g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * factor)
    b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * factor)

    return rgb_to_hex(r, g, b)


if __name__ == "__main__":
    main()