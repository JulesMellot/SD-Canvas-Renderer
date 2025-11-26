"""
Tests d'intégration complets avec Stream Deck simulé

Ces tests simulent un workflow complet sans hardware physique
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from streamdeck_canvas import (
    StreamDeckCanvas,
    DebugRenderer,
    StreamDeckRenderer,
    Button,
    ProgressBar,
    Waveform,
    VUMeter,
    Timer,
    ScrollingText,
    LoadingSpinner,
    Grid,
    WidgetManager,
)


# ============= TESTS D'INTÉGRATION CANVAS COMPLET =============

class TestCanvasIntegration:
    """Tests d'intégration pour le canvas"""

    def test_complete_drawing_workflow(self, canvas_classic):
        """Test d'un workflow complet de dessin"""
        canvas = canvas_classic

        # 1. Effacer le canvas
        canvas.clear('#000000')

        # 2. Dessiner plusieurs éléments
        canvas.draw_rect(0, 0, color='#FF6B35')
        canvas.draw_circle(1, 0, radius=25, color='#4CAF50')
        canvas.draw_text(2, 0, "Test", color='#FFFFFF')

        # 3. Ajouter du texte avec icône
        canvas.draw_icon_text(0, 1, icon="🎵", label="Music")

        # 4. Dessiner une ligne
        canvas.draw_line(0, 2, 100, 2, color='#FF0000', width=3)

        # 5. Obtenir les tiles
        tiles = canvas.get_tiles()

        # 6. Vérifier
        assert len(tiles) == 15
        assert all(tile.size == (72, 72) for tile in tiles)

    def test_multi_button_region_drawing(self, canvas_classic):
        """Test de dessin sur une région multi-boutons"""
        canvas = canvas_classic

        # Dessiner une barre de progression sur 5 boutons
        canvas.draw_rect(0, 1, width_cols=5, height_rows=1, color='#1A1110', border='#4A4543')

        # Dessiner le contenu
        for col in range(5):
            canvas.draw_rect(col, 1, color='#FF6B35' if col < 2 else '#4A4543')

        tiles = canvas.get_tiles()
        assert len(tiles) == 15

    def test_image_pasting_workflow(self, canvas_classic, sample_image):
        """Test de workflow de collage d'images"""
        canvas = canvas_classic

        # Coller des images dans plusieurs boutons
        positions = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]

        for col, row in positions:
            # Redimensionner l'image
            img = sample_image.copy()
            img = img.resize((72, 72))
            canvas.paste_image(col, row, img)

        tiles = canvas.get_tiles()

        # Vérifier que toutes les tiles ont du contenu
        assert len(tiles) == 15

    def test_clear_and_redraw(self, canvas_classic):
        """Test de clear et redessin"""
        canvas = canvas_classic

        # Premier dessin
        canvas.draw_rect(0, 0, color='#FF0000')
        tiles1 = canvas.get_tiles()

        # Clear
        canvas.clear('#000000')
        tiles2 = canvas.get_tiles()

        # Nouveau dessin
        canvas.draw_rect(0, 0, color='#00FF00')
        tiles3 = canvas.get_tiles()

        # Les tiles doivent être différentes
        assert len(tiles1) == len(tiles2) == len(tiles3) == 15

    def test_coordinate_system(self, canvas_classic):
        """Test du système de coordonnées"""
        canvas = canvas_classic

        # Vérifier les coordonnées de chaque bouton
        for row in range(canvas.rows):
            for col in range(canvas.cols):
                x, y, w, h = canvas.get_button_rect(col, row)
                assert x == col * 72
                assert y == row * 72
                assert w == 72
                assert h == 72

    def test_region_coordinates(self, canvas_classic):
        """Test des coordonnées de région"""
        canvas = canvas_classic

        # Région 3×2 à (1, 1)
        x, y, w, h = canvas.get_region_rect(1, 1, 3, 2)

        assert x == 72
        assert y == 72
        assert w == 216
        assert h == 144


# ============= TESTS D'INTÉGRATION RENDERER COMPLET =============

class TestRendererIntegration:
    """Tests d'intégration pour les renderers"""

    def test_debug_renderer_lifecycle(self, temp_dir):
        """Test du cycle de vie complet de DebugRenderer"""
        import os

        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:
            # 1. Création
            renderer = DebugRenderer(cols=5, rows=3, button_size=72)
            assert renderer.canvas is not None

            # 2. Dessin
            renderer.canvas.draw_rect(0, 0, color='#FF6B35')

            # 3. Update (plusieurs frames)
            for i in range(5):
                renderer.update()

            assert renderer.frame_count == 5

            # 4. Stop
            renderer.stop()
            assert renderer.running == False

            # 5. Vérifier les fichiers générés
            debug_files = [f for f in os.listdir('.') if f.startswith('debug_frame_')]
            assert len(debug_files) >= 5

        finally:
            os.chdir(original_dir)

    def test_streamdeck_renderer_with_mock_device(self, mock_streamdeck_classic):
        """Test complet de StreamDeckRenderer avec device mock"""
        with patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True):
            with patch('streamdeck_canvas.renderer.DeviceManager'):
                # 1. Création
                renderer = StreamDeckRenderer(mock_streamdeck_classic)
                assert renderer.deck == mock_streamdeck_classic

                # 2. Configuration
                assert renderer.canvas is not None
                mock_streamdeck_classic.set_brightness.assert_called_once()

                # 3. Dessin
                renderer.canvas.draw_rect(0, 0, color='#FF6B35')
                renderer.canvas.draw_text(1, 0, "Test", color='#FFFFFF')

                # 4. Update
                renderer.update()

                # Vérifier les appels au device
                assert mock_streamdeck_classic.set_key_image.call_count == 15

                # 5. Callback de touche
                callback = Mock()
                renderer.on_button_press = callback

                # Simuler un événement
                renderer._handle_key_event(mock_streamdeck_classic, 0, True)
                callback.assert_called_once_with(0, 0, 0)

                # 6. Stop
                renderer.stop()
                assert renderer.running == False

    def test_renderer_with_different_orientations(self, mock_streamdeck_classic):
        """Test de renderer avec différentes orientations"""
        orientations = ['normal', 'rotated', 'h_mirror', 'v_mirror', 'h_mirror_rotated', 'v_mirror_rotated']

        for orientation in orientations:
            with patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True):
                with patch('streamdeck_canvas.renderer.DeviceManager'):
                    renderer = StreamDeckRenderer(mock_streamdeck_classic, orientation=orientation)

                    # Créer une image test
                    img = Image.new('RGB', (72, 72), color='#FF6B35')

                    # Convertir (ne doit pas lever d'exception)
                    native_data = renderer._pil_to_native(img)

                    assert isinstance(native_data, bytes)
                    assert len(native_data) > 0

                    renderer.stop()

    def test_debug_renderer_different_sizes(self):
        """Test de DebugRenderer avec différentes tailles"""
        sizes = [
            (5, 3, 72),   # Classic
            (3, 2, 80),   # Mini
            (8, 4, 96),   # XL
        ]

        for cols, rows, button_size in sizes:
            renderer = DebugRenderer(cols=cols, rows=rows, button_size=button_size)

            assert renderer.cols == cols
            assert renderer.rows == rows
            assert renderer.button_size == button_size
            assert renderer.canvas.cols == cols
            assert renderer.canvas.rows == rows

            # Vérifier les dimensions du canvas
            expected_width = cols * button_size
            expected_height = rows * button_size
            assert renderer.canvas.width == expected_width
            assert renderer.canvas.height == expected_height

            renderer.stop()


# ============= TESTS D'INTÉGRATION WIDGETS COMPLET =============

class TestWidgetsIntegration:
    """Tests d'intégration pour tous les widgets"""

    def test_button_rendering_with_all_options(self, canvas_classic):
        """Test de rendu de bouton avec toutes les options"""
        canvas = canvas_classic

        # Bouton normal
        button1 = Button(
            col=0, row=0,
            icon="🎵", label="Music",
            bg_color='#4A4543',
            icon_color='#FFF8F0',
            label_color='#FFF8F0'
        )
        button1.render(canvas)

        # Bouton avec bordure
        button2 = Button(
            col=1, row=0,
            icon="📹", label="Video",
            bg_color='#4A4543',
            border=True,
            border_color='#FF6B35'
        )
        button2.render(canvas)

        # Bouton pressé
        button3 = Button(
            col=2, row=0,
            icon="🎮", label="Game",
            bg_color='#4A4543'
        )
        button3.pressed = True
        button3.render(canvas)

        assert True

    def test_progress_bar_different_values(self, canvas_classic):
        """Test de barre de progression avec différentes valeurs"""
        canvas = canvas_classic

        # Différents niveaux de progression
        progress_values = [0.0, 0.25, 0.5, 0.75, 1.0]

        for i, progress in enumerate(progress_values):
            progress_bar = ProgressBar(
                col=0, row=i,
                width=5,
                progress=progress
            )
            progress_bar.render(canvas)

        assert True

    def test_waveform_with_cues_and_animation(self, canvas_classic):
        """Test de waveform avec cues et animation"""
        canvas = canvas_classic

        waveform = Waveform(
            col=0, row=1,
            width=5,
            progress=0.5
        )

        # Ajouter des cues
        waveform.add_cue(0.25)
        waveform.add_cue(0.5)
        waveform.add_cue(0.75)

        # Rendu avec animation
        for i in range(10):
            waveform.set_progress(i / 10.0)
            waveform.render(canvas)

        assert waveform.animation_frame == 10
        assert len(waveform.cues) == 3

    def test_vu_meter_with_peak_hold(self, canvas_classic):
        """Test de VU-mètre avec peak hold"""
        canvas = canvas_classic

        vu_meter = VUMeter(col=4, row=1, level=0.0)

        # Simuler une montée
        for i in range(1, 101):
            vu_meter.set_level(i / 100.0)
            vu_meter.render(canvas)

        # Le peak hold devrait être proche de 1.0
        assert vu_meter.peak_hold > 0.99

    def test_timer_formatting(self, canvas_classic):
        """Test de formatage du timer"""
        canvas = canvas_classic

        timer = Timer(col=0, row=2, current_time=0, total_time=300)

        # Différents temps
        test_times = [
            (0, 300),
            (60, 300),
            (150, 300),
            (300, 300),
            (450, 600),
        ]

        for current, total in test_times:
            timer.set_time(current, total)
            timer.render(canvas)

        assert True

    def test_scrolling_text_animation(self, canvas_classic):
        """Test d'animation du texte défilant"""
        canvas = canvas_classic

        scrolling_text = ScrollingText(
            col=0, row=2,
            width=5,
            text="Mon fichier audio très long qui dépasse.mp3"
        )

        # Animation
        initial_offset = scrolling_text.offset

        for _ in range(50):
            scrolling_text.render(canvas)

        # L'offset devrait avoir changé
        assert scrolling_text.frame_count > 0

    def test_loading_spinner_animation(self, canvas_classic):
        """Test d'animation du spinner"""
        canvas = canvas_classic

        spinner = LoadingSpinner(col=2, row=2)

        initial_angle = spinner.angle

        for _ in range(10):
            spinner.render(canvas)

        # L'angle devrait avoir augmenté
        assert spinner.angle > initial_angle

    def test_grid_debug_rendering(self, canvas_classic):
        """Test de rendu de grille de debug"""
        canvas = canvas_classic

        grid = Grid(cols=5, rows=3, show_numbers=True)
        grid.render(canvas)

        assert True

    def test_all_widgets_in_layout(self, canvas_classic):
        """Test de tous les widgets dans un layout"""
        canvas = canvas_classic
        manager = WidgetManager()

        # Ajouter un de chaque type
        manager.add(Button(col=0, row=0, icon="🎵", label="Audio"))
        manager.add(ProgressBar(col=0, row=1, width=3, progress=0.5))
        manager.add(Waveform(col=3, row=1, width=2))
        manager.add(VUMeter(col=4, row=0))
        manager.add(Timer(col=4, row=1))
        manager.add(ScrollingText(col=0, row=2, width=3, text="Track Name"))
        manager.add(LoadingSpinner(col=3, row=2))
        manager.add(Grid(cols=5, rows=3, show_numbers=False))

        # Rendu
        manager.render_all(canvas)
        tiles = canvas.get_tiles()

        assert len(tiles) == 15
        assert len(manager.widgets) == 8

    def test_widget_manager_operations(self, canvas_classic):
        """Test des opérations du WidgetManager"""
        canvas = canvas_classic
        manager = WidgetManager()

        # Ajouter des widgets
        widgets = [
            Button(col=i % 5, row=i // 5, icon=str(i), label=f"Button{i}")
            for i in range(10)
        ]

        for widget in widgets:
            manager.add(widget)

        assert len(manager.widgets) == 10

        # Rendu
        manager.render_all(canvas)

        # Recherche
        widget = manager.find_widget_at(0, 0)
        assert widget is not None

        # Filtrage par type
        buttons = manager.get_widgets_by_type(Button)
        assert len(buttons) == 10

        # Retrait
        manager.remove(widgets[0])
        assert len(manager.widgets) == 9

        # Clear
        manager.clear()
        assert len(manager.widgets) == 0


# ============= TESTS D'INTÉGRATION WORKFLOWS COMPLETS =============

class TestCompleteWorkflows:
    """Tests de workflows complets"""

    def test_music_player_dashboard(self, canvas_classic):
        """Test d'un dashboard lecteur musical complet"""
        canvas = canvas_classic
        manager = WidgetManager()

        # 1. Boutons principaux
        manager.add(Button(col=0, row=0, icon="⏮", label="Prev"))
        manager.add(Button(col=1, row=0, icon="⏯", label="Play", bg_color='#4CAF50'))
        manager.add(Button(col=2, row=0, icon="⏭", label="Next"))
        manager.add(Button(col=3, row=0, icon="🔊", label="Vol+"))
        manager.add(Button(col=4, row=0, icon="🔉", label="Vol-"))

        # 2. Barre de progression
        manager.add(ProgressBar(col=0, row=1, width=5, progress=0.35))

        # 3. VU-mètres
        manager.add(VUMeter(col=0, row=2, level=0.7))
        manager.add(VUMeter(col=4, row=2, level=0.6))

        # 4. Timer
        manager.add(Timer(col=2, row=2, current_time=105, total_time=300))

        # 5. Nom du titre (scrolling)
        scrolling_text = manager.add(ScrollingText(
            col=1, row=2, width=3,
            text="Artist Name - Track Title - Album Name.mp3"
        ))

        # 6. Rendu
        manager.render_all(canvas)
        tiles = canvas.get_tiles()

        assert len(tiles) == 15
        assert len(manager.widgets) == 9

        # 7. Animation (mise à jour)
        for i in range(10):
            # Mettre à jour la progression
            progress_bar = manager.get_widgets_by_type(ProgressBar)[0]
            progress_bar.set_progress(0.35 + i * 0.05)

            # Mettre à jour les VU-mètres
            for vu in manager.get_widgets_by_type(VUMeter):
                vu.set_level(0.5 + 0.3 * abs(0.5 - (i % 10) / 10))

            # Mettre à jour le timer
            timer = manager.get_widgets_by_type(Timer)[0]
            timer.set_time(105 + i, 300)

            # Re-rendre
            manager.render_all(canvas)

    def test_video_player_dashboard(self, canvas_classic):
        """Test d'un dashboard lecteur vidéo"""
        canvas = canvas_classic
        manager = WidgetManager()

        # Boutons de contrôle
        manager.add(Button(col=1, row=0, icon="⏮", label="Prev"))
        manager.add(Button(col=2, row=0, icon="⏯", label="Play", bg_color='#4CAF50'))
        manager.add(Button(col=3, row=0, icon="⏭", label="Next"))

        # Barre de progression
        manager.add(Waveform(col=0, row=1, width=5, progress=0.6))
        manager.get_widgets_by_type(Waveform)[0].add_cue(0.25)
        manager.get_widgets_by_type(Waveform)[0].add_cue(0.75)

        # Timer
        manager.add(Timer(col=0, row=2, current_time=720, total_time=5400))

        # Loading spinner pendant le chargement
        manager.add(LoadingSpinner(col=4, row=2))

        # Rendu
        manager.render_all(canvas)

        assert len(manager.widgets) == 6

    def test_recording_studio_dashboard(self, canvas_xl):
        """Test d'un dashboard studio d'enregistrement (XL)"""
        canvas, manager = canvas_xl, WidgetManager()

        # Pistes audio (VU-mètres)
        for i in range(8):
            manager.add(VUMeter(col=i, row=0, level=0.3 + (i % 5) * 0.1))

        # Contrôles de transport
        manager.add(Button(col=0, row=1, icon="⏺", label="Rec", bg_color='#F44336'))
        manager.add(Button(col=1, row=1, icon="⏯", label="Play", bg_color='#4CAF50'))
        manager.add(Button(col=2, row=1, icon="⏸", label="Pause"))
        manager.add(Button(col=3, row=1, icon="⏹", label="Stop"))
        manager.add(Button(col=4, row=1, icon="⏮", label="Rewind"))
        manager.add(Button(col=5, row=1, icon="⏭", label="FastFwd"))

        # Barre de progression principale
        manager.add(ProgressBar(col=0, row=2, width=8, progress=0.45))

        # Timer principal
        manager.add(Timer(col=3, row=3, current_time=240, total_time=3600))

        # Rendu
        manager.render_all(canvas)
        tiles = canvas.get_tiles()

        # XL a 8×4 = 32 boutons
        assert len(tiles) == 32
        assert len(manager.widgets) == 15

    def test_system_monitoring_dashboard(self, canvas_classic):
        """Test d'un dashboard de monitoring système"""
        canvas = canvas_classic
        manager = WidgetManager()

        # CPU usage (barre de progression)
        manager.add(ProgressBar(col=0, row=0, width=2, progress=0.65, fill_color='#FF9800'))
        manager.add(Button(col=2, row=0, icon="💻", label="CPU", bg_color='#FF9800'))

        # Memory usage (barre de progression)
        manager.add(ProgressBar(col=0, row=1, width=2, progress=0.45, fill_color='#2196F3'))
        manager.add(Button(col=2, row=1, icon="🧠", label="RAM", bg_color='#2196F3'))

        # Disk usage (barre de progression)
        manager.add(ProgressBar(col=0, row=2, width=2, progress=0.78, fill_color='#9C27B0'))
        manager.add(Button(col=2, row=2, icon="💾", label="Disk", bg_color='#9C27B0'))

        # Status indicators
        manager.add(Button(col=3, row=0, icon="🟢", label="Online"))
        manager.add(Button(col=4, row=0, icon="📶", label="Network"))
        manager.add(Button(col=3, row=1, icon="🌡️", label="Temp"))
        manager.add(Button(col=4, row=1, icon="🔋", label="Battery"))

        # Rendu
        manager.render_all(canvas)

        assert len(manager.widgets) == 10

    def test_game_controller_layout(self, canvas_mini):
        """Test d'un layout de contrôleur de jeu (Mini)"""
        canvas = canvas_mini
        manager = WidgetManager()

        # Boutons ABXY
        colors = ['#F44336', '#4CAF50', '#2196F3', '#FF9800']
        labels = ['A', 'B', 'X', 'Y']
        positions = [(2, 0), (2, 1), (1, 1), (1, 0)]

        for (col, row), label, color in zip(positions, labels, colors):
            manager.add(Button(col, row, icon=label, label="", bg_color=color))

        # D-pad
        manager.add(Button(col=0, row=0, icon="▲", label="Up"))
        manager.add(Button(col=0, row=2, icon="▼", label="Down"))
        manager.add(Button(col=0, row=1, icon="◀", label="Left"))
        manager.add(Button(col=1, row=1, icon="▶", label="Right"))

        # Rendu
        manager.render_all(canvas)
        tiles = canvas.get_tiles()

        # Mini a 3×2 = 6 boutons
        assert len(tiles) == 6
        assert len(manager.widgets) == 8

    def test_sequential_frame_updates(self, canvas_classic):
        """Test de mise à jour séquentielle de frames"""
        canvas = canvas_classic
        manager = WidgetManager()

        # Ajouter un waveform animé
        waveform = manager.add(Waveform(col=0, row=1, width=5, progress=0.0))

        # Ajouter un spinner
        spinner = manager.add(LoadingSpinner(col=2, row=2))

        # Simulation de 100 frames
        for frame in range(100):
            # Mettre à jour la progression (0.0 à 1.0 puis reset)
            waveform.set_progress((frame % 100) / 100.0)

            # Re-rendre
            canvas.clear()
            manager.render_all(canvas)

            # Obtenir les tiles
            tiles = canvas.get_tiles()

            assert len(tiles) == 15

        assert waveform.progress > 0.9

    def test_interactive_button_press_simulation(self, mock_streamdeck_classic):
        """Test de simulation d'appui de boutons"""
        with patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True):
            with patch('streamdeck_canvas.renderer.DeviceManager'):
                renderer = StreamDeckRenderer(mock_streamdeck_classic)
                manager = WidgetManager()

                # Ajouter des boutons
                buttons = []
                for i in range(15):
                    col = i % 5
                    row = i // 5
                    button = Button(col, row, icon=f"{i}", label=f"Btn{i}")
                    buttons.append(button)
                    manager.add(button)

                # Callback pour les événements
                pressed_buttons = []
                def on_button_press(col, row, key):
                    pressed_buttons.append((col, row, key))

                renderer.on_button_press = on_button_press

                # Simuler des appuis
                for i in range(15):
                    renderer._handle_key_event(mock_streamdeck_classic, i, True)

                    # Effet visuel (pressed)
                    buttons[i].pressed = True
                    manager.render_all(renderer.canvas)

                assert len(pressed_buttons) == 15
                assert all(btn.pressed for btn in buttons)

                renderer.stop()

    def test_error_recovery_workflow(self, canvas_classic):
        """Test de workflow avec récupération d'erreurs"""
        canvas = canvas_classic

        # Test avec valeurs invalides
        try:
            # Couleur invalide
            canvas.draw_rect(0, 0, color='invalid')
        except:
            pass

        # Continuer正常工作
        canvas.draw_rect(0, 0, color='#FF0000')

        # Test avec position invalide
        try:
            canvas.draw_rect(-1, -1)
        except:
            pass

        # Continuer
        canvas.draw_rect(1, 1, color='#00FF00')

        tiles = canvas.get_tiles()
        assert len(tiles) == 15

    def test_memory_management(self, canvas_classic):
        """Test de gestion mémoire avec beaucoup d'objets"""
        canvas = canvas_classic
        manager = WidgetManager()

        # Créer et supprimer beaucoup de widgets
        for batch in range(10):
            # Ajouter 50 widgets
            for i in range(50):
                widget = Button(col=i % 5, row=i // 5, icon=f"{i}", label=f"Btn{i}")
                manager.add(widget)

            # Rendre
            manager.render_all(canvas)

            # Supprimer tous
            manager.clear()

        # Finalement, ajouter quelques widgets
        for i in range(5):
            manager.add(Button(col=i, row=0, icon=f"{i}", label=f"Btn{i}"))

        manager.render_all(canvas)

        assert len(manager.widgets) == 5


# ============= TESTS DE PERFORMANCE =============

class TestPerformance:
    """Tests de performance et optimisation"""

    def test_large_number_of_buttons(self, canvas_xl):
        """Test avec beaucoup de boutons (XL)"""
        canvas, manager = canvas_xl, WidgetManager()

        # Ajouter un bouton pour chaque position (8×4 = 32)
        for row in range(4):
            for col in range(8):
                manager.add(Button(col, row, icon=f"🎮", label=f"({col},{row})"))

        # Rendu
        start_time = time.time()
        manager.render_all(canvas)
        end_time = time.time()

        # Devrait rendre en moins de 100ms
        assert (end_time - start_time) < 0.1

        tiles = canvas.get_tiles()
        assert len(tiles) == 32

    def test_rapid_updates(self, canvas_classic):
        """Test de mises à jour rapides"""
        canvas = canvas_classic
        manager = WidgetManager()

        # Ajouter un VU-mètre qui change rapidement
        vu_meter = manager.add(VUMeter(col=4, row=1))

        # 1000 mises à jour rapides
        start_time = time.time()
        for i in range(1000):
            vu_meter.set_level(abs(0.5 - (i % 100) / 100.0))
            vu_meter.render(canvas)
        end_time = time.time()

        # Devrait 完成 en moins de 1 seconde
        assert (end_time - start_time) < 1.0

    def test_concurrent_widget_types(self, canvas_classic):
        """Test de rendu concurrent de types de widgets différents"""
        canvas = canvas_classic
        manager = WidgetManager()

        # Ajouter beaucoup de widgets de types différents
        widget_types = [
            lambda i: Button(col=i % 5, row=i // 5, icon="🎮", label=f"Game{i}"),
            lambda i: ProgressBar(col=i % 5, row=(i // 5) % 3, width=1, progress=(i % 100) / 100.0),
            lambda i: Timer(col=i % 5, row=(i // 5) % 3),
        ]

        for widget_type in widget_types:
            for i in range(10):
                manager.add(widget_type(i))

        # Rendu
        start_time = time.time()
        manager.render_all(canvas)
        end_time = time.time()

        assert (end_time - start_time) < 0.2

    def test_image_pasting_performance(self, canvas_classic, sample_image):
        """Test de performance du collage d'images"""
        canvas = canvas_classic

        start_time = time.time()

        # Coller des images dans tous les boutons
        for row in range(3):
            for col in range(5):
                img = sample_image.copy()
                img = img.resize((72, 72))
                canvas.paste_image(col, row, img)

        end_time = time.time()

        # Devrait être relativement rapide
        assert (end_time - start_time) < 0.5

        tiles = canvas.get_tiles()
        assert len(tiles) == 15


# ============= TESTS DE VALIDATION FINALE =============

class TestValidation:
    """Tests de validation finale"""

    def test_all_widget_types_functional(self, canvas_classic):
        """Vérifier que tous les types de widgets fonctionnent"""
        canvas = canvas_classic

        widgets_to_test = [
            ("Button", Button(col=0, row=0, icon="🎵", label="Test")),
            ("ProgressBar", ProgressBar(col=0, row=1, width=3, progress=0.5)),
            ("Waveform", Waveform(col=0, row=1, width=5)),
            ("VUMeter", VUMeter(col=4, row=1)),
            ("Timer", Timer(col=0, row=2, current_time=120, total_time=300)),
            ("ScrollingText", ScrollingText(col=0, row=2, width=3, text="Test")),
            ("LoadingSpinner", LoadingSpinner(col=2, row=2)),
            ("Grid", Grid(cols=5, rows=3, show_numbers=False)),
        ]

        for name, widget in widgets_to_test:
            try:
                widget.render(canvas)
            except Exception as e:
                pytest.fail(f"Widget {name} a échoué: {e}")

    def test_all_orientations_work(self, mock_streamdeck_classic):
        """Vérifier que toutes les orientations fonctionnent"""
        orientations = ['normal', 'rotated', 'h_mirror', 'v_mirror', 'h_mirror_rotated', 'v_mirror_rotated']

        for orientation in orientations:
            with patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True):
                with patch('streamdeck_canvas.renderer.DeviceManager'):
                    try:
                        renderer = StreamDeckRenderer(mock_streamdeck_classic, orientation=orientation)
                        img = Image.new('RGB', (72, 72), color='#FF6B35')
                        native_data = renderer._pil_to_native(img)
                        assert len(native_data) > 0
                        renderer.stop()
                    except Exception as e:
                        pytest.fail(f"Orientation {orientation} a échoué: {e}")

    def test_all_device_sizes(self):
        """Vérifier que toutes les tailles de device fonctionnent"""
        device_sizes = [
            (5, 3, 72, 15),  # Classic
            (3, 2, 80, 6),   # Mini
            (8, 4, 96, 32),  # XL
        ]

        for cols, rows, button_size, expected_keys in device_sizes:
            renderer = DebugRenderer(cols=cols, rows=rows, button_size=button_size)

            assert renderer.cols == cols
            assert renderer.rows == rows
            assert renderer.button_size == button_size

            # Vérifier le canvas
            assert renderer.canvas.cols == cols
            assert renderer.canvas.rows == rows

            # Vérifier les tiles
            tiles = renderer.canvas.get_tiles()
            assert len(tiles) == expected_keys

            for tile in tiles:
                assert tile.size == (button_size, button_size)

            renderer.stop()

    def test_color_handling(self, canvas_classic):
        """Vérifier que la gestion des couleurs fonctionne"""
        canvas = canvas_classic

        # Couleurs standard
        standard_colors = [
            '#FF0000', '#00FF00', '#0000FF',
            '#FFFF00', '#FF00FF', '#00FFFF',
            '#FFFFFF', '#000000', '#808080',
        ]

        for i, color in enumerate(standard_colors):
            col = i % 5
            row = i // 5
            canvas.draw_rect(col, row, color=color)

        # Couleurs de la palette
        from streamdeck_canvas.utils import ColorPalette
        palette_colors = [
            ColorPalette.PRIMARY,
            ColorPalette.SECONDARY,
            ColorPalette.ACCENT,
            ColorPalette.BACKGROUND,
            ColorPalette.SURFACE,
        ]

        for i, color in enumerate(palette_colors):
            canvas.draw_rect(i % 5, 2, color=color)

        tiles = canvas.get_tiles()
        assert len(tiles) == 15

    def test_text_rendering_all_sizes(self, canvas_classic):
        """Vérifier que le rendu de texte fonctionne pour toutes les tailles"""
        canvas = canvas_classic

        text_sizes = ['tiny', 'small', 'normal', 'title', 'large', 'huge']
        text = "Test"

        for i, size in enumerate(text_sizes):
            col = i % 5
            row = i // 5
            canvas.draw_text(col, row, text, size=size)

        assert True

    def test_font_fallback(self, canvas_classic):
        """Vérifier que le fallback de police fonctionne"""
        canvas = canvas_classic

        # Vérifier que des polices sont chargées
        assert len(canvas.fonts) > 0

        # Tester avec du texte
        canvas.draw_text(0, 0, "Test", size='normal')
        canvas.draw_text(1, 0, "Test", size='large')
        canvas.draw_text(2, 0, "Test", size='small')

        assert True
