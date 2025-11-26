#!/usr/bin/env python3
"""
Stream Deck Canvas Renderer - Dashboard Système
Monitoring système avec animations et indicateurs en temps réel
"""

import time
import math
import random
from streamdeck_canvas import StreamDeckCanvas
from streamdeck_canvas.renderer import DebugRenderer
from streamdeck_canvas.widgets import (
    Button, ProgressBar, VUMeter, Timer, ScrollingText, WidgetManager
)
from streamdeck_canvas.utils import ColorPalette, FPSCounter, format_bytes


def main():
    """Dashboard système avec CPU, mémoire, réseau, et processus"""

    renderer = DebugRenderer(cols=5, rows=3, button_size=72)
    canvas = renderer.canvas
    widgets = WidgetManager()

    # === Informations système (première rangée) ===

    # Nom du système
    system_name = widgets.add(Button(0, 0, "🖥️", "SYSTEM",
                                   bg_color=ColorPalette.PRIMARY))

    # Uptime
    uptime_widget = widgets.add(Timer(1, 0, current_time=0.0,
                                    color=ColorPalette.TEXT_PRIMARY,
                                    bg_color=ColorPalette.BACKGROUND))

    # Bouton de refresh
    refresh_btn = widgets.add(Button(2, 0, "🔄", "REFRESH",
                              bg_color=ColorPalette.SUCCESS))

    # Notifications
    notif_btn = widgets.add(Button(3, 0, "🔔", "ALERTS",
                               bg_color=ColorPalette.SURFACE))

    # Settings
    settings_btn = widgets.add(Button(4, 0, "⚙️", "CONFIG",
                                    bg_color=ColorPalette.SURFACE))

    # === Ressources système (deuxième rangée) ===

    # CPU Usage
    cpu_label = widgets.add(Button(0, 1, "CPU", "",
                                 bg_color=ColorPalette.BACKGROUND))
    cpu_bar = widgets.add(ProgressBar(1, 1, width=2, progress=0.0,
                                    bg_color=ColorPalette.BACKGROUND,
                                    fill_color=ColorPalette.WARNING))

    # Memory Usage
    mem_label = widgets.add(Button(3, 1, "MEM", "",
                                 bg_color=ColorPalette.BACKGROUND))
    mem_bar = widgets.add(ProgressBar(4, 1, width=1, progress=0.0,
                                    bg_color=ColorPalette.BACKGROUND,
                                    fill_color=ColorPalette.PRIMARY))

    # === Processus et réseau (troisième rangée) ===

    # Processus actifs
    process_info = widgets.add(ScrollingText(0, 2, width=2,
                                          text="Processes: 142 running",
                                          bg_color=ColorPalette.BACKGROUND))

    # Network activity
    network_label = widgets.add(Button(2, 2, "🌐", "NET",
                                    bg_color=ColorPalette.BACKGROUND))
    network_bar = widgets.add(ProgressBar(3, 2, width=1, progress=0.0,
                                       bg_color=ColorPalette.BACKGROUND,
                                       fill_color=ColorPalette.INFO))

    # Disk usage
    disk_label = widgets.add(Button(4, 2, "💾", "DISK",
                                bg_color=ColorPalette.BACKGROUND))

    # Simulation de données système
    system_start_time = time.time()
    fps_counter = FPSCounter()

    # Données simulées
    cpu_usage = 0.0
    memory_usage = 0.0
    network_usage = 0.0
    process_count = 142
    alerts_count = 3

    print("📊 Stream Deck System Dashboard - Démarrage")
    print("   Monitoring: CPU, Memory, Network, Processes")

    try:
        frame_count = 0
        while frame_count < 600:  # 40 secondes

            frame_start = time.time()
            current_time = time.time()

            # === Simulation des données système ===

            # CPU Usage (variation réaliste)
            cpu_target = 0.3 + 0.4 * math.sin(current_time * 0.2) + random.uniform(-0.05, 0.05)
            cpu_usage = cpu_usage * 0.9 + cpu_target * 0.1  # Lissage
            cpu_usage = max(0.0, min(1.0, cpu_usage))
            cpu_bar.set_progress(cpu_usage)

            # Couleur du CPU selon le niveau
            if cpu_usage > 0.8:
                cpu_label.bg_color = ColorPalette.ERROR
            elif cpu_usage > 0.6:
                cpu_label.bg_color = ColorPalette.WARNING
            else:
                cpu_label.bg_color = ColorPalette.SUCCESS

            # Memory Usage (croissance lente avec pics)
            memory_target = 0.4 + 0.2 * math.sin(current_time * 0.1) + random.uniform(-0.02, 0.02)
            memory_usage = memory_usage * 0.95 + memory_target * 0.05
            memory_usage = max(0.0, min(1.0, memory_usage))
            mem_bar.set_progress(memory_usage)

            # Network Activity (bursts intermittents)
            if random.random() < 0.1:  # 10% de chance de burst
                network_usage = random.uniform(0.6, 1.0)
            else:
                network_usage *= 0.8  # Décroissance rapide
            network_bar.set_progress(network_usage)

            # Process count (variation)
            process_change = random.choice([-1, 0, 0, 1, 1])
            process_count = max(120, min(200, process_count + process_change))
            mem_usage_gb = int(8 * memory_usage)  # Simulation 8GB total
            process_info.set_text(f"Processes: {process_count} | MEM: {mem_usage_gb}GB")

            # Alerts (variation)
            if random.random() < 0.02:  # 2% de chance nouvelle alerte
                alerts_count = min(9, alerts_count + 1)
            elif random.random() < 0.01 and alerts_count > 0:  # 1% de chance résolution
                alerts_count -= 1

            notif_btn.label = f"{alerts_count}" if alerts_count > 0 else "OK"
            notif_btn.bg_color = ColorPalette.ERROR if alerts_count > 5 else (
                ColorPalette.WARNING if alerts_count > 0 else ColorPalette.SUCCESS
            )

            # Uptime
            uptime_seconds = current_time - system_start_time
            uptime_widget.set_time(uptime_seconds)

            # === Animations et interactions ===

            # Animation du refresh
            if frame_count % 45 == 0:  # Toutes les 3 secondes
                refresh_btn.pressed = True
            elif frame_count % 45 == 2:
                refresh_btn.pressed = False

            # Animation de network si activité
            network_label.pressed = network_usage > 0.3
            network_label.bg_color = ColorPalette.INFO if network_usage > 0.1 else ColorPalette.BACKGROUND

            # Disk usage (simulation)
            disk_usage = 0.6 + 0.1 * math.sin(current_time * 0.05)
            if disk_usage > 0.85:
                disk_label.bg_color = ColorPalette.ERROR
            elif disk_usage > 0.75:
                disk_label.bg_color = ColorPalette.WARNING
            else:
                disk_label.bg_color = ColorPalette.SUCCESS

            # === Rendu ===
            canvas.clear(ColorPalette.BACKGROUND)

            # Ajout d'un indicateur visuel pour CPU
            cpu_label.label = f"{int(cpu_usage * 100)}%"
            mem_label.label = f"{int(memory_usage * 100)}%"
            network_label.label = f"{int(network_usage * 100)}%"

            widgets.render_all(canvas)

            # Afficher les stats système dans la console
            current_fps = fps_counter.update()
            if frame_count % 60 == 0:  # Toutes les 4 secondes
                cpu_percent = int(cpu_usage * 100)
                mem_percent = int(memory_usage * 100)
                net_percent = int(network_usage * 100)
                print(f"📊 CPU: {cpu_percent}% | MEM: {mem_percent}% | "
                      f"NET: {net_percent}% | Processes: {process_count} | "
                      f"Alerts: {alerts_count} | FPS: {current_fps:.1f}")

            renderer.update()

            # Frame timing
            frame_duration = time.time() - frame_start
            sleep_time = max(0, (1/15) - frame_duration)
            if sleep_time > 0:
                time.sleep(sleep_time)

            frame_count += 1

    except KeyboardInterrupt:
        print("\n⏹️  Dashboard interrompu")

    print(f"📊 Dashboard système terminé | Frames: {frame_count} | "
          f"Uptime: {format_time(time.time() - system_start_time)} | "
          f"FPS moyen: {fps_counter.get_fps():.1f}")


def format_time(seconds: float) -> str:
    """Formatage du temps avec heures si nécessaire"""
    if seconds >= 3600:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"
    else:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"


if __name__ == "__main__":
    main()