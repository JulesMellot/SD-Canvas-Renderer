#!/usr/bin/env python3
"""
Stream Deck Canvas Renderer - Moniteur Audio
Simulation d'un moniteur audio pour streaming/production
"""

import time
import math
import random
from streamdeck_canvas import StreamDeckCanvas
from streamdeck_canvas.renderer import DebugRenderer
from streamdeck_canvas.widgets import (
    Button, Waveform, VUMeter, Timer, ScrollingText, WidgetManager
)
from streamdeck_canvas.utils import ColorPalette, FPSCounter, format_time


def main():
    """Moniteur audio avec waveform, VU-mètres, et contrôles"""

    # Renderer debug
    renderer = DebugRenderer(cols=5, rows=3, button_size=72)
    canvas = renderer.canvas
    widgets = WidgetManager()

    # === Contrôles de transport (première rangée) ===

    # Boutons de transport
    play_btn = widgets.add(Button(0, 0, "⏸️", "PAUSE",
                                bg_color=ColorPalette.PRIMARY))
    stop_btn = widgets.add(Button(1, 0, "⏹️", "STOP",
                                bg_color=ColorPalette.SURFACE))
    rec_btn = widgets.add(Button(2, 0, "⏺️", "REC",
                                bg_color=ColorPalette.ERROR))

    # Timer d'enregistrement/lecture
    timer_widget = widgets.add(Timer(3, 0, current_time=0.0, total_time=180.0,
                                   color=ColorPalette.TEXT_PRIMARY,
                                   bg_color=ColorPalette.BACKGROUND))

    # Bouton de monitoring
    monitor_btn = widgets.add(Button(4, 0, "🎧", "MON",
                                   bg_color=ColorPalette.SUCCESS))

    # === Section audio principale (deuxième rangée) ===

    # Waveform principale sur 3 boutons
    main_waveform = widgets.add(Waveform(0, 1, width=3, progress=0.0,
                                       bg_color=ColorPalette.BACKGROUND,
                                       played_color=ColorPalette.SUCCESS,
                                       unplayed_color=ColorPalette.SURFACE))

    # VU-mètres stéréo
    vu_left = widgets.add(VUMeter(3, 1, level=0.0,
                                 bg_color=ColorPalette.BACKGROUND))
    vu_right = widgets.add(VUMeter(4, 1, level=0.0,
                                  bg_color=ColorPalette.BACKGROUND))

    # === Section inférieure (troisième rangée) ===

    # Nom du fichier/piste en cours
    track_name = widgets.add(ScrollingText(0, 2, width=3,
                                         text="Now_Playing: Epic_Soundtrack_Final_Edit.wav",
                                         bg_color=ColorPalette.BACKGROUND))

    # Indicateurs de statut
    peak_indicator = widgets.add(Button(3, 2, "🔴", "PEAK",
                                      bg_color=ColorPalette.BACKGROUND))

    rms_indicator = widgets.add(Button(4, 2, "📊", "RMS",
                                    bg_color=ColorPalette.BACKGROUND))

    # États
    is_playing = False
    is_recording = False
    current_time = 0.0
    track_duration = 180.0  # 3 minutes

    # Timers et compteurs
    fps_counter = FPSCounter()
    audio_timer = time.time()
    last_peak_time = 0

    print("🎵 Stream Deck Audio Monitor - Démarrage")
    print("   Features: Transport Controls, Waveform, VU-Meters, Track Info")

    try:
        frame_count = 0
        while frame_count < 450:  # 30 secondes de démo

            frame_start = time.time()
            elapsed = time.time() - audio_timer

            # === Simulation de l'audio ===

            # Génération de niveaux audio réalistes
            if is_playing or is_recording:
                # Simulation de signal audio avec variation
                base_level = 0.3 + 0.2 * math.sin(elapsed * 0.5)
                noise = random.uniform(-0.05, 0.05)
                transient = random.choice([0, 0, 0, 0.15])  # 25% de chance de transient

                left_level = min(1.0, base_level + noise + transient)
                right_level = min(1.0, base_level - noise * 0.5 + transient * 0.8)

                # Détection de peaks
                peak_threshold = 0.95
                if left_level > peak_threshold or right_level > peak_threshold:
                    peak_indicator.bg_color = ColorPalette.ERROR
                    last_peak_time = time.time()
                    peak_icon = "🔴"
                else:
                    peak_indicator.bg_color = ColorPalette.BACKGROUND
                    peak_icon = "⚪"

                peak_indicator.icon = peak_icon

                # Mise à jour des VU-mètres
                vu_left.set_level(left_level)
                vu_right.set_level(right_level)

                # Mise à jour du waveform
                if is_playing:
                    current_time += 1/15  # 15 FPS
                    if current_time >= track_duration:
                        current_time = 0.0

                waveform_progress = current_time / track_duration
                main_waveform.set_progress(waveform_progress)

            else:
                # Niveaux au repos
                vu_left.set_level(0.0)
                vu_right.set_level(0.0)
                peak_indicator.bg_color = ColorPalette.BACKGROUND
                peak_indicator.icon = "⚪"

            # === Gestion des contrôles ===

            # Simulation d'actions automatiques pour la démo
            if frame_count == 30:  # Démarrer la lecture
                is_playing = True
                play_btn.icon = "▶️"
                play_btn.label = "PLAY"
                play_btn.bg_color = ColorPalette.SUCCESS
                audio_timer = time.time()
                current_time = 0.0

            elif frame_count == 60:  # Ajouter un cue
                main_waveform.add_cue(0.15)

            elif frame_count == 90:  # Ajouter un autre cue
                main_waveform.add_cue(0.45)

            elif frame_count == 120:  # Démarrer l'enregistrement
                is_recording = True
                rec_btn.bg_color = ColorPalette.ERROR
                rec_btn.pressed = True

            elif frame_count == 180:  # Pause
                is_playing = False
                play_btn.icon = "⏸️"
                play_btn.label = "PAUSE"
                play_btn.bg_color = ColorPalette.PRIMARY

            elif frame_count == 210:  # Reprendre
                is_playing = True
                play_btn.icon = "▶️"
                play_btn.label = "PLAY"
                play_btn.bg_color = ColorPalette.SUCCESS

            elif frame_count == 270:  # Stopper l'enregistrement
                is_recording = False
                rec_btn.bg_color = ColorPalette.SURFACE
                rec_btn.pressed = False

            elif frame_count == 300:  # Stop
                is_playing = False
                play_btn.icon = "⏸️"
                play_btn.label = "PAUSE"
                play_btn.bg_color = ColorPalette.PRIMARY
                current_time = 0.0
                main_waveform.set_progress(0.0)

            elif frame_count == 330:  # Redémarrer
                is_playing = True
                play_btn.icon = "▶️"
                play_btn.label = "PLAY"
                play_btn.bg_color = ColorPalette.SUCCESS
                audio_timer = time.time()

            # Mise à jour des labels
            rec_btn.label = "REC" if is_recording else "REC"
            monitor_btn.pressed = is_playing or is_recording

            # Mise à jour du timer
            timer_widget.set_time(current_time, track_duration)

            # Changement de nom de piste
            if frame_count % 150 == 0 and frame_count > 0:
                tracks = [
                    "Now_Playing: Epic_Soundtrack_Final_Edit.wav",
                    "Podcast_Episode_42_Interview_Master.wav",
                    "Live_Stream_Recording_Session_Take_03.wav",
                    "Music_Production_Beats_Instrumental.wav"
                ]
                track_name.set_text(random.choice(tracks))

            # === Rendu ===
            canvas.clear(ColorPalette.BACKGROUND)
            widgets.render_all(canvas)

            # Stats
            current_fps = fps_counter.update()
            if frame_count % 45 == 0:  # Toutes les 3 secondes
                status = "PLAYING" if is_playing else "STOPPED"
                if is_recording:
                    status += " + REC"
                print(f"🎵 {status} | FPS: {current_fps:.1f} | "
                      f"Time: {format_time(current_time)}/{format_time(track_duration)} | "
                      f"Peak: {'ON' if time.time() - last_peak_time < 1.0 else 'OFF'}")

            renderer.update()

            # Frame timing
            frame_duration = time.time() - frame_start
            sleep_time = max(0, (1/15) - frame_duration)
            if sleep_time > 0:
                time.sleep(sleep_time)

            frame_count += 1

    except KeyboardInterrupt:
        print("\n⏹️  Monitor audio interrompu")

    print(f"🎵 Monitor audio terminé | Frames: {frame_count} | "
          f"FPS moyen: {fps_counter.get_fps():.1f}")


if __name__ == "__main__":
    main()