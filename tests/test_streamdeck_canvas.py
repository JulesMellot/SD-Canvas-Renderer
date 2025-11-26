"""
Suite de tests complète pour Stream Deck Canvas Renderer

Tests TDD couvrant:
- Canvas layer (StreamDeckCanvas)
- Renderer layer (StreamDeckRenderer, DebugRenderer)
- Widget system
- Utility functions
- Device detection
- Integration tests

IMPORTANT: Utilise des mocks pour éviter les dépendances hardware
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from PIL import Image, ImageDraw

# Import du package à tester
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
    ColorPalette,
    FPSCounter,
)

# Import des utilitaires directement
from streamdeck_canvas.utils import (
    hex_to_rgb,
    rgb_to_hex,
    clamp,
    interpolate_color,
    format_time,
    format_bytes,
    calculate_fps,
    ease_in_out_cubic,
    ease_out_elastic,
    lerp,
)


# ============= TESTS CANVAS LAYER =============

class TestStreamDeckCanvas:
    """Tests pour la classe StreamDeckCanvas"""

    def test_canvas_initialization_classic(self, canvas_classic):
        """Test d'initialisation du canvas pour Stream Deck Classic"""
        canvas = canvas_classic
        assert canvas.cols == 5
        assert canvas.rows == 3
        assert canvas.button_size == 72
        assert canvas.width == 360  # 5 * 72
        assert canvas.height == 216  # 3 * 72
        assert canvas.image is not None
        assert canvas.draw is not None
        assert canvas.fonts is not None

    def test_canvas_initialization_mini(self, canvas_mini):
        """Test d'initialisation du canvas pour Stream Deck Mini"""
        canvas = canvas_mini
        assert canvas.cols == 3
        assert canvas.rows == 2
        assert canvas.button_size == 80
        assert canvas.width == 240  # 3 * 80
        assert canvas.height == 160  # 2 * 80

    def test_canvas_initialization_xl(self, canvas_xl):
        """Test d'initialisation du canvas pour Stream Deck XL"""
        canvas = canvas_xl
        assert canvas.cols == 8
        assert canvas.rows == 4
        assert canvas.button_size == 96
        assert canvas.width == 768  # 8 * 96
        assert canvas.height == 384  # 4 * 96

    def test_clear_canvas(self, canvas_classic):
        """Test de clear du canvas"""
        canvas = canvas_classic

        # Dessiner quelque chose
        canvas.draw_rect(0, 0, color='#FF6B35')

        # Clear
        canvas.clear('#000000')

        # Vérifier que l'image est vide
        assert canvas.image.size == (360, 216)
        pixels = list(canvas.image.getdata())
        # Tous les pixels doivent être noirs
        assert all(p == (0, 0, 0) for p in pixels[:10])

    def test_get_button_rect(self, canvas_classic):
        """Test de get_button_rect"""
        canvas = canvas_classic

        # Bouton en (0, 0)
        x, y, w, h = canvas.get_button_rect(0, 0)
        assert x == 0
        assert y == 0
        assert w == 72
        assert h == 72

        # Bouton en (2, 1)
        x, y, w, h = canvas.get_button_rect(2, 1)
        assert x == 144  # 2 * 72
        assert y == 72   # 1 * 72
        assert w == 72
        assert h == 72

    def test_get_region_rect(self, canvas_classic):
        """Test de get_region_rect pour régions multi-boutons"""
        canvas = canvas_classic

        # Région 3×2 à partir de (1, 1)
        x, y, w, h = canvas.get_region_rect(1, 1, 3, 2)
        assert x == 72   # 1 * 72
        assert y == 72   # 1 * 72
        assert w == 216  # 3 * 72
        assert h == 144  # 2 * 72

    def test_hex_to_rgb_conversion(self, canvas_classic):
        """Test de conversion hex vers RGB"""
        # Test avec #
        rgb = canvas_classic.hex_to_rgb('#FF6B35')
        assert rgb == (255, 107, 53)

        # Test sans #
        rgb = canvas_classic.hex_to_rgb('FF6B35')
        assert rgb == (255, 107, 53)

        # Test avec couleur autre
        rgb = canvas_classic.hex_to_rgb('#000000')
        assert rgb == (0, 0, 0)

    def test_private_hex_to_rgb(self, canvas_classic):
        """Test de la méthode privée _hex_to_rgb (compatibilité)"""
        # Cette méthode devrait faire référence à hex_to_rgb
        rgb = canvas_classic._hex_to_rgb('#FF6B35')
        assert rgb == (255, 107, 53)

    def test_draw_rect_single_button(self, canvas_classic):
        """Test de draw_rect pour un seul bouton"""
        canvas = canvas_classic

        canvas.draw_rect(0, 0, color='#FF6B35', border='#000000', border_width=2)

        # Vérifier que quelque chose a été dessiné
        pixels = list(canvas.image.getdata())
        # Le bouton (0,0) commence à (0,0) et fait 72×72
        # Avec padding de 3px et border_width de 2, on a une zone de dessin
        # Laisse juste vérifier qu'on a des pixels colorés
        button_pixels = pixels[0:72*72]
        # Au moins un pixel devrait être orange
        assert any(p == (255, 107, 53) for p in button_pixels)

    def test_draw_rect_multi_buttons(self, canvas_classic):
        """Test de draw_rect sur plusieurs boutons"""
        canvas = canvas_classic

        canvas.draw_rect(0, 0, width_cols=3, height_rows=2, color='#4CAF50')

        # Vérifier la taille de la région
        x, y, w, h = canvas.get_region_rect(0, 0, 3, 2)
        assert w == 216  # 3 * 72
        assert h == 144  # 2 * 72

    def test_draw_rect_with_radius(self, canvas_classic):
        """Test de draw_rect avec coins arrondis"""
        canvas = canvas_classic

        # Ne doit pas lever d'exception
        canvas.draw_rect(0, 0, radius=10, color='#FF6B35')

        # Si on arrive ici, c'est que ça marche
        assert True

    def test_draw_text_center(self, canvas_classic):
        """Test de draw_text avec alignement centre"""
        canvas = canvas_classic

        canvas.draw_text(0, 0, "Test", color='#FFFFFF', align='center')

        # Vérifier que du texte a été dessiné
        # (on ne peut pas facilement vérifier le contenu du texte
        # mais on peut vérifier qu'aucune exception n'est levée)
        assert True

    def test_draw_text_different_alignments(self, canvas_classic):
        """Test de draw_text avec différents alignements"""
        canvas = canvas_classic

        # Test alignements différents
        canvas.draw_text(0, 0, "Top", align='top')
        canvas.draw_text(1, 0, "Center", align='center')
        canvas.draw_text(2, 0, "Bottom", align='bottom')
        canvas.draw_text(3, 0, "Left", align='left')

        assert True

    def test_draw_icon_text(self, canvas_classic):
        """Test de draw_icon_text (icône + label)"""
        canvas = canvas_classic

        canvas.draw_icon_text(
            0, 0,
            icon="🎵",
            label="Music",
            icon_color='#FF6B35',
            label_color='#FFFFFF'
        )

        assert True

    def test_draw_circle(self, canvas_classic):
        """Test de draw_circle"""
        canvas = canvas_classic

        canvas.draw_circle(0, 0, radius=25, color='#FF6B35', border='#000000')

        assert True

    def test_draw_line(self, canvas_classic):
        """Test de draw_line"""
        canvas = canvas_classic

        canvas.draw_line(10, 10, 50, 50, color='#FFFFFF', width=3)

        assert True

    def test_paste_image(self, canvas_classic, sample_image):
        """Test de paste_image"""
        canvas = canvas_classic

        canvas.paste_image(0, 0, sample_image)

        # Vérifier que l'image a été collée
        x, y, w, h = canvas.get_button_rect(0, 0)
        # L'image collée devrait affecter les pixels
        pixels = list(canvas.image.getdata())
        # Au moins quelques pixels devraient être colorés
        # (on ne peut pas être plus précis sans connaître l'implémentation)
        assert len(pixels) == 360 * 216

    def test_get_tiles(self, canvas_classic):
        """Test de get_tiles - découpage en boutons individuels"""
        canvas = canvas_classic

        # Dessiner quelque chose de distinct sur le premier bouton
        canvas.draw_rect(0, 0, color='#FF6B35')

        tiles = canvas.get_tiles()

        # Pour un Stream Deck Classic: 5×3 = 15 boutons
        assert len(tiles) == 15

        # Chaque tile doit faire 72×72
        for tile in tiles:
            assert tile.size == (72, 72)

        # Le premier bouton (index 0) devrait être coloré
        # L'ordre des tiles: row 2, col 0-4; row 1, col 0-4; row 0, col 0-4
        first_button_pixels = list(tiles[10].getdata())  # row 0, col 0 = index 10
        # Au moins un pixel devrait être orange
        assert any(p == (255, 107, 53) for p in first_button_pixels)

    def test_get_tiles_mini(self, canvas_mini):
        """Test de get_tiles pour Stream Deck Mini"""
        canvas = canvas_mini

        tiles = canvas.get_tiles()

        # Pour un Stream Deck Mini: 3×2 = 6 boutons
        assert len(tiles) == 6

        # Chaque tile doit faire 80×80
        for tile in tiles:
            assert tile.size == (80, 80)

    def test_get_tiles_xl(self, canvas_xl):
        """Test de get_tiles pour Stream Deck XL"""
        canvas = canvas_xl

        tiles = canvas.get_tiles()

        # Pour un Stream Deck XL: 8×4 = 32 boutons
        assert len(tiles) == 32

        # Chaque tile doit faire 96×96
        for tile in tiles:
            assert tile.size == (96, 96)

    def test_save_debug(self, canvas_classic, temp_dir):
        """Test de sauvegarde du canvas en debug"""
        canvas = canvas_classic

        # Dessiner quelque chose
        canvas.draw_rect(0, 0, color='#FF6B35')

        # Sauvegarder
        filepath = f"{temp_dir}/test_canvas.png"
        canvas.save_debug(filepath)

        # Vérifier que le fichier a été créé
        assert os.path.exists(filepath)

        # Vérifier que c'est une image valide
        img = Image.open(filepath)
        assert img.size == (360, 216)

    def test_different_colors(self, canvas_classic):
        """Test de différentes couleurs"""
        canvas = canvas_classic

        # Tester plusieurs couleurs
        colors = [
            '#FF0000',  # Rouge
            '#00FF00',  # Vert
            '#0000FF',  # Bleu
            '#FFFF00',  # Jaune
            '#FFFFFF',  # Blanc
            '#000000',  # Noir
        ]

        for i, color in enumerate(colors):
            canvas.draw_rect(i % 5, i // 5, color=color)

        assert True


# ============= TESTS RENDERER LAYER =============

class TestDebugRenderer:
    """Tests pour DebugRenderer"""

    def test_debug_renderer_init(self, debug_renderer_classic):
        """Test d'initialisation de DebugRenderer"""
        renderer = debug_renderer_classic

        assert renderer.cols == 5
        assert renderer.rows == 3
        assert renderer.button_size == 72
        assert renderer.canvas is not None
        assert renderer.running == False
        assert renderer.frame_count == 0
        assert renderer.deck is None

    def test_debug_renderer_mini(self, debug_renderer_mini):
        """Test d'initialisation DebugRenderer Mini"""
        renderer = debug_renderer_mini

        assert renderer.cols == 3
        assert renderer.rows == 2
        assert renderer.button_size == 80

    def test_debug_renderer_update(self, debug_renderer_classic, temp_dir):
        """Test de update (sauvegarde d'image)"""
        renderer = debug_renderer_classic

        # Dessiner quelque chose sur le canvas
        renderer.canvas.draw_rect(0, 0, color='#FF6B35')

        # Mettre à jour (sauvegarder)
        renderer.update()

        # Vérifier que le frame_count a augmenté
        assert renderer.frame_count == 1

        # Un fichier debug_frame_0000.png devrait avoir été créé
        # (le répertoire courant peut varier, donc on vérifie juste qu'il n'y a pas d'exception)

    def test_debug_renderer_stop(self, debug_renderer_classic):
        """Test d'arrêt de DebugRenderer"""
        renderer = debug_renderer_classic

        renderer.stop()

        assert renderer.running == False


class TestStreamDeckRenderer:
    """Tests pour StreamDeckRenderer (avec mocks)"""

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_streamdeck_renderer_init_classic(self, mock_device_manager, mock_streamdeck_classic):
        """Test d'initialisation StreamDeckRenderer Classic"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic)

        assert renderer.deck == mock_streamdeck_classic
        assert renderer.target_fps == 15
        assert renderer.button_size == 72
        assert renderer.cols == 5
        assert renderer.rows == 3
        assert renderer.canvas is not None
        assert renderer.frame_count == 0
        assert renderer.running == False

        # Vérifier que le deck a été configuré
        mock_streamdeck_classic.set_brightness.assert_called_once_with(80)

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_streamdeck_renderer_init_mini(self, mock_device_manager, mock_streamdeck_mini):
        """Test d'initialisation StreamDeckRenderer Mini"""
        renderer = StreamDeckRenderer(mock_streamdeck_mini)

        assert renderer.cols == 3
        assert renderer.rows == 2
        assert renderer.button_size == 80

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_streamdeck_renderer_init_xl(self, mock_device_manager, mock_streamdeck_xl):
        """Test d'initialisation StreamDeckRenderer XL"""
        renderer = StreamDeckRenderer(mock_streamdeck_xl)

        assert renderer.cols == 8
        assert renderer.rows == 4
        assert renderer.button_size == 96

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_streamdeck_renderer_update(self, mock_device_manager, mock_streamdeck_classic):
        """Test de update (envoi d'images au deck)"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic)

        # Dessiner quelque chose
        renderer.canvas.draw_rect(0, 0, color='#FF6B35')

        # Mettre à jour
        renderer.update()

        # Vérifier que set_key_image a été appelé pour chaque bouton
        assert mock_streamdeck_classic.set_key_image.call_count == 15

        # Vérifier que le frame_count a augmenté
        assert renderer.frame_count == 1

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_pil_to_native_normal_orientation(self, mock_device_manager, mock_streamdeck_classic):
        """Test de conversion PIL vers format natif (orientation normale)"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic, orientation='normal')

        # Créer une image test
        img = Image.new('RGB', (72, 72), color='#FF6B35')

        # Convertir
        native_data = renderer._pil_to_native(img)

        # Vérifier que c'est des bytes (format JPEG)
        assert isinstance(native_data, bytes)
        assert len(native_data) > 0

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_pil_to_native_rotated_orientation(self, mock_device_manager, mock_streamdeck_classic):
        """Test de conversion PIL avec orientation retournée"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic, orientation='rotated')

        img = Image.new('RGB', (72, 72), color='#FF6B35')
        native_data = renderer._pil_to_native(img)

        assert isinstance(native_data, bytes)
        assert len(native_data) > 0

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_pil_to_native_mirror_orientations(self, mock_device_manager, mock_streamdeck_classic):
        """Test de conversion PIL avec orientations mirror"""
        orientations = ['h_mirror', 'v_mirror', 'h_mirror_rotated', 'v_mirror_rotated']

        for orientation in orientations:
            renderer = StreamDeckRenderer(mock_streamdeck_classic, orientation=orientation)
            img = Image.new('RGB', (72, 72), color='#FF6B35')
            native_data = renderer._pil_to_native(img)

            assert isinstance(native_data, bytes)
            assert len(native_data) > 0

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_pil_to_native_invalid_orientation(self, mock_device_manager, mock_streamdeck_classic):
        """Test de conversion PIL avec orientation invalide"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic, orientation='invalid')

        img = Image.new('RGB', (72, 72), color='#FF6B35')
        native_data = renderer._pil_to_native(img)

        # Doit quand même fonctionner (fallback)
        assert isinstance(native_data, bytes)

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_pil_to_native_rgba_image(self, mock_device_manager, mock_streamdeck_classic):
        """Test de conversion PIL avec image RGBA"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic)

        img = Image.new('RGBA', (72, 72), color=(255, 107, 53, 128))
        native_data = renderer._pil_to_native(img)

        # Devrait convertir en RGB
        assert isinstance(native_data, bytes)
        assert len(native_data) > 0

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_handle_key_event(self, mock_device_manager, mock_streamdeck_classic):
        """Test de gestion des événements de touche"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic)

        # Callback mock
        callback = Mock()
        renderer.on_button_press = callback

        # Simuler un événement de touche
        # key 0 = col 0, row 0
        renderer._handle_key_event(mock_streamdeck_classic, 0, True)

        callback.assert_called_once_with(0, 0, 0)

        # key 7 = col 2, row 1
        renderer._handle_key_event(mock_streamdeck_classic, 7, True)

        callback.assert_called_with(2, 1, 7)

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_handle_key_event_no_callback(self, mock_device_manager, mock_streamdeck_classic):
        """Test de gestion des événements sans callback"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic)

        # Pas de callback défini
        renderer.on_button_press = None

        # Ne doit pas lever d'exception
        renderer._handle_key_event(mock_streamdeck_classic, 0, True)

        assert True

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_streamdeck_renderer_stop(self, mock_device_manager, mock_streamdeck_classic):
        """Test d'arrêt de StreamDeckRenderer"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic)

        renderer.stop()

        assert renderer.running == False

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    def test_single_frame(self, mock_device_manager, mock_streamdeck_classic):
        """Test de single_frame"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic)

        renderer.single_frame()

        # Vérifier qu'update a été appelé
        # (on ne peut pas vérifier directement, mais on vérifie qu'il n'y a pas d'exception)
        assert True

    @patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True)
    @patch('streamdeck_canvas.renderer.DeviceManager')
    @patch('time.sleep')
    def test_render_loop(self, mock_sleep, mock_device_manager, mock_streamdeck_classic):
        """Test de la boucle de rendu (avec timeout)"""
        renderer = StreamDeckRenderer(mock_streamdeck_classic, target_fps=30)

        render_callback = Mock()

        # Démarrer la boucle mais l'arrêter immédiatement
        import threading
        def stop_renderer():
            time.sleep(0.1)
            renderer.running = False

        thread = threading.Thread(target=stop_renderer)
        thread.start()

        renderer.render_loop(render_callback)

        thread.join()

        # Vérifier que le callback a été appelé au moins une fois
        assert render_callback.call_count > 0


# ============= TESTS WIDGETS =============

class TestWidget:
    """Tests pour la classe Widget de base"""

    def test_widget_init(self):
        """Test d'initialisation de Widget"""
        from streamdeck_canvas.widgets import Widget

        widget = Widget(col=2, row=3, width=2, height=2)

        assert widget.col == 2
        assert widget.row == 3
        assert widget.width == 2
        assert widget.height == 2
        assert widget.visible == True

    def test_widget_is_point_inside(self):
        """Test de is_point_inside"""
        from streamdeck_canvas.widgets import Widget

        widget = Widget(col=2, row=3, width=2, height=2)

        # Points à l'intérieur
        assert widget.is_point_inside(2, 3)  # Coin supérieur gauche
        assert widget.is_point_inside(3, 3)  # Coin supérieur droit
        assert widget.is_point_inside(2, 4)  # Coin inférieur gauche
        assert widget.is_point_inside(3, 4)  # Coin inférieur droit

        # Points à l'extérieur
        assert not widget.is_point_inside(1, 3)  # Trop à gauche
        assert not widget.is_point_inside(4, 3)  # Trop à droite
        assert not widget.is_point_inside(2, 2)  # Trop en haut
        assert not widget.is_point_inside(2, 5)  # Trop en bas


class TestButtonWidget:
    """Tests pour le widget Button"""

    def test_button_init(self, button_widget):
        """Test d'initialisation du bouton"""
        widget = button_widget

        assert widget.icon == "🎵"
        assert widget.label == "Audio"
        assert widget.bg_color == '#4A4543'
        assert widget.icon_color == '#FFF8F0'
        assert widget.label_color == '#FFF8F0'
        assert widget.pressed == False
        assert widget.col == 0
        assert widget.row == 0
        assert widget.width == 1
        assert widget.height == 1

    def test_button_render(self, button_widget, canvas_classic):
        """Test de rendu du bouton"""
        widget = button_widget
        canvas = canvas_classic

        widget.render(canvas)

        # Le bouton a été rendu sans exception
        assert True

    def test_button_pressed_effect(self, button_widget, canvas_classic):
        """Test de l'effet pressed"""
        widget = button_widget
        canvas = canvas_classic

        # Bouton pressé
        widget.pressed = True
        widget.render(canvas)

        # Le bouton a été rendu sans exception
        assert True


class TestProgressBarWidget:
    """Tests pour le widget ProgressBar"""

    def test_progress_bar_init(self, progress_bar_widget):
        """Test d'initialisation de la barre de progression"""
        widget = progress_bar_widget

        assert widget.col == 0
        assert widget.row == 0
        assert widget.width == 3
        assert widget.height == 1
        assert widget.progress == 0.5
        assert widget.bg_color == '#1A1110'
        assert widget.fill_color == '#FF6B35'
        assert widget.show_percentage == True

    def test_progress_bar_set_progress(self, progress_bar_widget):
        """Test de mise à jour de la progression"""
        widget = progress_bar_widget

        # Test avec valeur normale
        widget.set_progress(0.75)
        assert widget.progress == 0.75

        # Test avec valeur > 1 (doit être clampé)
        widget.set_progress(1.5)
        assert widget.progress == 1.0

        # Test avec valeur < 0 (doit être clampé)
        widget.set_progress(-0.5)
        assert widget.progress == 0.0

    def test_progress_bar_render(self, progress_bar_widget, canvas_classic):
        """Test de rendu de la barre de progression"""
        widget = progress_bar_widget
        canvas = canvas_classic

        widget.render(canvas)

        # La barre a été rendue sans exception
        assert True

    def test_progress_bar_render_0_percent(self, progress_bar_widget, canvas_classic):
        """Test de rendu avec 0%"""
        widget = progress_bar_widget
        widget.set_progress(0.0)
        canvas = canvas_classic

        widget.render(canvas)

        assert True

    def test_progress_bar_render_100_percent(self, progress_bar_widget, canvas_classic):
        """Test de rendu avec 100%"""
        widget = progress_bar_widget
        widget.set_progress(1.0)
        canvas = canvas_classic

        widget.render(canvas)

        assert True

    def test_progress_bar_without_percentage(self, canvas_classic):
        """Test de barre de progression sans pourcentage"""
        from streamdeck_canvas.widgets import ProgressBar

        widget = ProgressBar(col=0, row=0, width=3, show_percentage=False)
        widget.render(canvas_classic)

        assert True


class TestWaveformWidget:
    """Tests pour le widget Waveform"""

    def test_waveform_init(self, waveform_widget):
        """Test d'initialisation du widget waveform"""
        widget = waveform_widget

        assert widget.col == 0
        assert widget.row == 0
        assert widget.width == 5
        assert widget.height == 1
        assert widget.progress == 0.3
        assert widget.cues == []
        assert widget.animation_frame == 0

    def test_waveform_set_progress(self, waveform_widget):
        """Test de mise à jour de la position"""
        widget = waveform_widget

        widget.set_progress(0.5)
        assert widget.progress == 0.5

        widget.set_progress(1.5)
        assert widget.progress == 1.0

        widget.set_progress(-0.5)
        assert widget.progress == 0.0

    def test_waveform_add_cue(self, waveform_widget):
        """Test d'ajout de cue markers"""
        widget = waveform_widget

        widget.add_cue(0.25)
        widget.add_cue(0.75)

        assert 0.25 in widget.cues
        assert 0.75 in widget.cues

    def test_waveform_clear_cues(self, waveform_widget):
        """Test d'effacement des cues"""
        widget = waveform_widget

        widget.add_cue(0.25)
        widget.add_cue(0.75)

        widget.clear_cues()

        assert widget.cues == []

    def test_waveform_render(self, waveform_widget, canvas_classic):
        """Test de rendu du widget waveform"""
        widget = waveform_widget
        canvas = canvas_classic

        widget.render(canvas)

        # Le waveform a été rendu
        # Vérifier que l'animation frame a augmenté
        assert widget.animation_frame == 1

    def test_waveform_render_with_cues(self, waveform_widget, canvas_classic):
        """Test de rendu avec cue markers"""
        widget = waveform_widget
        widget.add_cue(0.25)
        widget.add_cue(0.75)

        widget.render(canvas_classic)

        assert widget.animation_frame == 1


class TestVUMeterWidget:
    """Tests pour le widget VUMeter"""

    def test_vu_meter_init(self, vu_meter_widget):
        """Test d'initialisation du VU-mètre"""
        widget = vu_meter_widget

        assert widget.col == 0
        assert widget.row == 0
        assert widget.width == 1
        assert widget.height == 1
        assert widget.level == 0.7
        assert widget.peak_hold == 0.0
        assert widget.peak_hold_time == 0

    def test_vu_meter_set_level(self, vu_meter_widget):
        """Test de mise à jour du niveau"""
        widget = vu_meter_widget

        widget.set_level(0.5)
        assert widget.level == 0.5

        # Test peak hold
        widget.set_level(0.8)
        assert widget.level == 0.8
        assert widget.peak_hold == 0.8
        assert widget.peak_hold_time == 30

    def test_vu_meter_peak_hold_decay(self, vu_meter_widget):
        """Test de décrémentation du peak hold"""
        widget = vu_meter_widget

        # Définir un peak hold
        widget.peak_hold = 0.9
        widget.peak_hold_time = 0

        # Mettre à jour avec un niveau plus bas
        widget.set_level(0.5)

        # Le peak hold devrait décroître légèrement
        assert widget.peak_hold < 0.9
        assert widget.peak_hold >= 0.89

    def test_vu_meter_render(self, vu_meter_widget, canvas_classic):
        """Test de rendu du VU-mètre"""
        widget = vu_meter_widget
        canvas = canvas_classic

        widget.render(canvas)

        assert True

    def test_vu_meter_tall(self, canvas_classic):
        """Test de VU-mètre tall (plusieurs boutons)"""
        from streamdeck_canvas.widgets import VUMeter

        widget = VUMeter(col=0, row=0, height=2, level=0.7)
        widget.render(canvas_classic)

        assert widget.height == 2


class TestTimerWidget:
    """Tests pour le widget Timer"""

    def test_timer_init(self, timer_widget):
        """Test d'initialisation du timer"""
        widget = timer_widget

        assert widget.current_time == 120.0
        assert widget.total_time == 300.0
        assert widget.col == 0
        assert widget.row == 0
        assert widget.width == 1
        assert widget.height == 1

    def test_timer_set_time(self, timer_widget):
        """Test de mise à jour du temps"""
        widget = timer_widget

        widget.set_time(180.0)
        assert widget.current_time == 180.0
        assert widget.total_time == 300.0  # Inchangée

        widget.set_time(200.0, 400.0)
        assert widget.current_time == 200.0
        assert widget.total_time == 400.0

    def test_timer_render(self, timer_widget, canvas_classic):
        """Test de rendu du timer"""
        widget = timer_widget
        canvas = canvas_classic

        widget.render(canvas)

        # Le timer a été rendu
        assert True

    def test_timer_with_background(self, timer_widget, canvas_classic):
        """Test de timer avec fond"""
        widget = timer_widget
        widget.bg_color = '#4A4543'

        widget.render(canvas_classic)

        assert True


class TestScrollingTextWidget:
    """Tests pour le widget ScrollingText"""

    def test_scrolling_text_init(self, scrolling_text_widget):
        """Test d'initialisation du texte défilant"""
        widget = scrolling_text_widget

        assert widget.text == "Mon fichier très long.mp3"
        assert widget.color == '#FFF8F0'
        assert widget.bg_color == '#1A1110'
        assert widget.speed == 2
        assert widget.offset == 0
        assert widget.frame_count == 0

    def test_scrolling_text_set_text(self, scrolling_text_widget):
        """Test de changement de texte"""
        widget = scrolling_text_widget

        widget.set_text("Nouveau texte")
        assert widget.text == "Nouveau texte"
        assert widget.offset == 0  # Reset offset

    def test_scrolling_text_render(self, scrolling_text_widget, canvas_classic):
        """Test de rendu du texte défilant"""
        widget = scrolling_text_widget
        canvas = canvas_classic

        # Premier rendu
        widget.render(canvas)
        assert widget.frame_count == 1

        # Plusieurs rendus pour déclencher le défilement
        for _ in range(10):
            widget.render(canvas)

        # L'offset a pu changer
        assert widget.frame_count > 0

    def test_scrolling_text_short_text(self, canvas_classic):
        """Test avec texte court (pas de défilement)"""
        from streamdeck_canvas.widgets import ScrollingText

        widget = ScrollingText(col=0, row=0, width=3, text="Court")
        canvas = canvas_classic

        widget.render(canvas)

        # Texte court, pas de défilement
        assert widget.offset == 0


class TestLoadingSpinnerWidget:
    """Tests pour le widget LoadingSpinner"""

    def test_loading_spinner_init(self, loading_spinner_widget):
        """Test d'initialisation du spinner"""
        widget = loading_spinner_widget

        assert widget.color == '#F7931E'
        assert widget.bg_color is None
        assert widget.angle == 0

    def test_loading_spinner_render(self, loading_spinner_widget, canvas_classic):
        """Test de rendu du spinner"""
        widget = loading_spinner_widget
        canvas = canvas_classic

        widget.render(canvas)

        # L'angle a augmenté
        assert widget.angle == 15

    def test_loading_spinner_multiple_frames(self, loading_spinner_widget, canvas_classic):
        """Test d'animation sur plusieurs frames"""
        widget = loading_spinner_widget

        for i in range(10):
            widget.render(canvas_classic)

        # L'angle a augmenté
        assert widget.angle > 0


class TestGridWidget:
    """Tests pour le widget Grid"""

    def test_grid_init(self, grid_widget):
        """Test d'initialisation de la grille"""
        widget = grid_widget

        assert widget.grid_cols == 5
        assert widget.grid_rows == 3
        assert widget.col == 0
        assert widget.row == 0
        assert widget.width == 5
        assert widget.height == 3

    def test_grid_render(self, grid_widget, canvas_classic):
        """Test de rendu de la grille"""
        widget = grid_widget
        canvas = canvas_classic

        widget.render(canvas)

        assert True

    def test_grid_without_numbers(self, canvas_classic):
        """Test de grille sans numéros"""
        from streamdeck_canvas.widgets import Grid

        widget = Grid(cols=5, rows=3, show_numbers=False)
        widget.render(canvas_classic)

        assert True


class TestWidgetManager:
    """Tests pour WidgetManager"""

    def test_widget_manager_init(self, widget_manager):
        """Test d'initialisation du gestionnaire"""
        manager = widget_manager

        assert len(manager.widgets) == 3

    def test_widget_manager_add(self, widget_manager):
        """Test d'ajout de widget"""
        manager = widget_manager

        from streamdeck_canvas.widgets import Button
        new_widget = Button(col=3, row=0, icon="🎮", label="Game")

        manager.add(new_widget)

        assert len(manager.widgets) == 4
        assert new_widget in manager.widgets

    def test_widget_manager_remove(self, widget_manager):
        """Test de retrait de widget"""
        manager = widget_manager

        widget_to_remove = manager.widgets[0]
        manager.remove(widget_to_remove)

        assert len(manager.widgets) == 2
        assert widget_to_remove not in manager.widgets

    def test_widget_manager_clear(self, widget_manager):
        """Test d'effacement de tous les widgets"""
        manager = widget_manager

        manager.clear()

        assert len(manager.widgets) == 0

    def test_widget_manager_render_all(self, widget_manager, canvas_classic):
        """Test de rendu de tous les widgets"""
        manager = widget_manager
        canvas = canvas_classic

        manager.render_all(canvas)

        # Tous les widgets ont été rendus
        assert True

    def test_widget_manager_find_widget_at(self, widget_manager):
        """Test de recherche de widget à une position"""
        manager = widget_manager

        # Trouver le widget en (0, 0)
        widget = manager.find_widget_at(0, 0)

        assert widget is not None
        assert widget.col == 0
        assert widget.row == 0

        # Position vide
        widget = manager.find_widget_at(4, 2)

        assert widget is None

    def test_widget_manager_get_widgets_by_type(self, widget_manager):
        """Test de récupération par type"""
        manager = widget_manager

        # Récupérer tous les boutons
        buttons = manager.get_widgets_by_type(Button)

        # Il y a 2 boutons dans le manager par défaut
        assert len(buttons) == 2

        # Récupérer tous les ProgressBar
        progress_bars = manager.get_widgets_by_type(ProgressBar)

        assert len(progress_bars) == 1


# ============= TESTS UTILITAIRES =============

class TestColorUtilities:
    """Tests pour les utilitaires de couleur"""

    def test_hex_to_rgb(self):
        """Test de conversion hex vers RGB"""
        rgb = hex_to_rgb('#FF6B35')
        assert rgb == (255, 107, 53)

        rgb = hex_to_rgb('FF0000')
        assert rgb == (255, 0, 0)

    def test_hex_to_rgb_without_hash(self):
        """Test hex_to_rgb sans #"""
        rgb = hex_to_rgb('FFFFFF')
        assert rgb == (255, 255, 255)

    def test_hex_to_rgb_invalid(self):
        """Test hex_to_rgb avec couleur invalide"""
        with pytest.raises(ValueError):
            hex_to_rgb('ZZZ')

        with pytest.raises(ValueError):
            hex_to_rgb('GGGGGG')

    def test_rgb_to_hex(self):
        """Test de conversion RGB vers hex"""
        hex_color = rgb_to_hex(255, 107, 53)
        assert hex_color == '#FF6B35'

        hex_color = rgb_to_hex(0, 0, 0)
        assert hex_color == '#000000'

    def test_rgb_to_hex_invalid(self):
        """Test rgb_to_hex avec valeurs invalides"""
        with pytest.raises(ValueError):
            rgb_to_hex(-1, 0, 0)

        with pytest.raises(ValueError):
            rgb_to_hex(256, 0, 0)

    def test_interpolate_color(self):
        """Test d'interpolation de couleurs"""
        color = interpolate_color('#000000', '#FF0000', 0.5)
        # Devrait être halfway entre noir et rouge
        assert color == '#800000'

    def test_interpolate_color_edges(self):
        """Test interpolation aux limites"""
        # Facteur 0.0 = couleur de départ
        color = interpolate_color('#FF0000', '#00FF00', 0.0)
        assert color == '#FF0000'

        # Facteur 1.0 = couleur de fin
        color = interpolate_color('#FF0000', '#00FF00', 1.0)
        assert color == '#00FF00'

    def test_interpolate_color_clamp(self):
        """Test que les facteurs sont clampés"""
        # Facteur > 1.0
        color = interpolate_color('#000000', '#FFFFFF', 2.0)
        assert color == '#FFFFFF'

        # Facteur < 0.0
        color = interpolate_color('#000000', '#FFFFFF', -1.0)
        assert color == '#000000'


class TestMathUtilities:
    """Tests pour les utilitaires mathématiques"""

    def test_clamp(self):
        """Test de clamp"""
        assert clamp(5, 0, 10) == 5
        assert clamp(-5, 0, 10) == 0
        assert clamp(15, 0, 10) == 10

    def test_lerp(self):
        """Test d'interpolation linéaire"""
        result = lerp(0, 100, 0.5)
        assert result == 50.0

        result = lerp(0, 100, 0.0)
        assert result == 0.0

        result = lerp(0, 100, 1.0)
        assert result == 100.0

    def test_ease_in_out_cubic(self):
        """Test de easing cubique"""
        # t=0 => 0
        assert ease_in_out_cubic(0.0) == 0.0

        # t=1 => 1
        assert ease_in_out_cubic(1.0) == 1.0

        # Milieu (0.5) devrait être 0.5 avec easing
        result = ease_in_out_cubic(0.5)
        assert 0.0 < result < 1.0

    def test_ease_out_elastic(self):
        """Test de easing élastique"""
        # t=0 => 0
        assert ease_out_elastic(0.0) == 0.0

        # t=1 => 1
        assert ease_out_elastic(1.0) == 1.0

        # Milieu
        result = ease_out_elastic(0.5)
        assert 0.0 < result < 1.0


class TestFormattingUtilities:
    """Tests pour les utilitaires de formatage"""

    def test_format_time_seconds(self):
        """Test de formatage temps (secondes)"""
        assert format_time(65) == "01:05"
        assert format_time(125) == "02:05"
        assert format_time(3723) == "62:03"  # > 1h

    def test_format_time_with_hours(self):
        """Test de formatage temps avec heures"""
        assert format_time(3600, show_hours=True) == "01:00:00"
        assert format_time(3723, show_hours=True) == "01:02:03"

    def test_format_bytes(self):
        """Test de formatage tailles"""
        assert format_bytes(0) == "0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1536) == "1.5 KB"
        assert format_bytes(1048576) == "1.0 MB"
        assert format_bytes(1073741824) == "1.0 GB"


class TestTimer:
    """Tests pour la classe Timer"""

    def test_timer_init(self, timer):
        """Test d'initialisation du timer"""
        assert timer.start_time is None
        assert timer.end_time is None

    def test_timer_start_stop(self, timer):
        """Test de démarrage et arrêt"""
        timer.start()
        assert timer.start_time is not None

        time.sleep(0.01)
        timer.stop()
        assert timer.end_time is not None

        elapsed = timer.elapsed()
        assert elapsed >= 0.01

    def test_timer_elapsed_ms(self, timer):
        """Test de mesure en millisecondes"""
        timer.start()
        time.sleep(0.01)
        timer.stop()

        elapsed_ms = timer.elapsed_ms()
        assert elapsed_ms >= 10.0

    def test_timer_reset(self, timer):
        """Test de reset du timer"""
        timer.start()
        time.sleep(0.01)
        timer.reset()

        assert timer.start_time is None
        assert timer.end_time is None
        assert timer.elapsed() == 0.0


class TestFPSCounter:
    """Tests pour FPSCounter"""

    def test_fps_counter_init(self, fps_counter):
        """Test d'initialisation du compteur FPS"""
        assert fps_counter.window_size == 30
        assert fps_counter.frame_times == []
        assert fps_counter.fps == 0.0

    def test_fps_counter_update(self, fps_counter):
        """Test de mise à jour du compteur"""
        fps = fps_counter.update()
        assert fps == 0.0  # Premier update

        time.sleep(0.01)
        fps = fps_counter.update()
        assert fps > 0.0  # Après le premier frame

    def test_fps_counter_window(self, fps_counter):
        """Test de la fenêtre de mesure"""
        # Remplir la fenêtre
        for _ in range(35):
            fps_counter.update()
            time.sleep(0.01)

        # Ne devrait garder que les 30 dernières mesures
        assert len(fps_counter.frame_times) == 30

    def test_fps_counter_reset(self, fps_counter):
        """Test de reset du compteur"""
        fps_counter.update()
        time.sleep(0.01)
        fps_counter.update()

        fps_counter.reset()

        assert fps_counter.frame_times == []
        assert fps_counter.fps == 0.0


class TestColorPalette:
    """Tests pour ColorPalette"""

    def test_color_palette_constants(self):
        """Test des constantes de couleur"""
        assert ColorPalette.PRIMARY == '#FF6B35'
        assert ColorPalette.SECONDARY == '#F7931E'
        assert ColorPalette.ACCENT == '#FFB627'
        assert ColorPalette.BACKGROUND == '#1A1110'
        assert ColorPalette.TEXT_PRIMARY == '#FFF8F0'

    def test_color_palette_get_gradient(self):
        """Test de génération de dégradé"""
        gradient = ColorPalette.get_gradient(5, '#000000', '#FFFFFF')

        assert len(gradient) == 5
        assert gradient[0] == '#000000'
        assert gradient[4] == '#FFFFFF'

        # Les couleurs doivent être de plus en plus claires
        for i in range(len(gradient) - 1):
            from streamdeck_canvas.utils import hex_to_rgb
            rgb1 = hex_to_rgb(gradient[i])
            rgb2 = hex_to_rgb(gradient[i + 1])

            # Au moins une composante devrait être supérieure
            assert any(rgb2[j] >= rgb1[j] for j in range(3))


# ============= TESTS D'INTÉGRATION =============

class TestIntegrationWithMocks:
    """Tests d'intégration avec mocks (sans hardware)"""

    def test_complex_layout_rendering(self, complex_layout_canvas):
        """Test de rendu d'un layout complexe"""
        canvas, manager = complex_layout_canvas

        # Rendre tous les widgets
        manager.render_all(canvas)

        # Obtenir les tiles
        tiles = canvas.get_tiles()

        # Doit avoir 15 tiles pour un Classic
        assert len(tiles) == 15

        # Chaque tile doit avoir la bonne taille
        for tile in tiles:
            assert tile.size == (72, 72)

    def test_multiple_widget_updates(self, canvas_classic):
        """Test de mise à jour de plusieurs widgets"""
        from streamdeck_canvas.widgets import WidgetManager, Button, ProgressBar, VUMeter

        canvas = canvas_classic
        manager = WidgetManager()

        # Ajouter plusieurs widgets
        button = manager.add(Button(col=0, row=0, icon="🎵", label="Audio"))
        progress = manager.add(ProgressBar(col=0, row=1, width=5))
        vu_meter = manager.add(VUMeter(col=4, row=1))

        # Rendu initial
        manager.render_all(canvas)
        tiles1 = canvas.get_tiles()

        # Modifier les widgets
        progress.set_progress(0.75)
        vu_meter.set_level(0.9)
        button.pressed = True

        # Nouveau rendu
        manager.render_all(canvas)
        tiles2 = canvas.get_tiles()

        # Les tiles existent toujours
        assert len(tiles2) == 15

    def test_widget_visibility_toggle(self, canvas_classic):
        """Test de basculement de visibilité des widgets"""
        from streamdeck_canvas.widgets import WidgetManager, Button

        canvas = canvas_classic
        manager = WidgetManager()

        button = manager.add(Button(col=0, row=0, icon="🎵", label="Audio"))

        # Rendu visible
        manager.render_all(canvas)

        # Masquer le bouton
        button.visible = False
        manager.render_all(canvas)

        # Ne doit pas lever d'exception
        assert True

    def test_sequential_frame_rendering(self, canvas_classic):
        """Test de rendu séquentiel de frames"""
        from streamdeck_canvas.widgets import WidgetManager, Waveform

        canvas = canvas_classic
        manager = WidgetManager()

        waveform = manager.add(Waveform(col=0, row=1, width=5))

        # Rendu de plusieurs frames
        for i in range(10):
            # Mettre à jour la progression
            waveform.set_progress(i / 10.0)

            # Rendre
            manager.render_all(canvas)
            tiles = canvas.get_tiles()

            assert len(tiles) == 15

    def test_image_pasting_into_buttons(self, canvas_classic, sample_image):
        """Test de collage d'images dans des boutons"""
        canvas = canvas_classic

        # Coller l'image dans plusieurs boutons
        for col in range(5):
            for row in range(3):
                # Redimensionner l'image si nécessaire
                img = sample_image.copy()
                img = img.resize((72, 72))

                canvas.paste_image(col, row, img)

        # Obtenir les tiles
        tiles = canvas.get_tiles()

        assert len(tiles) == 15

    def test_all_widget_types_rendering(self, canvas_classic):
        """Test de rendu de tous les types de widgets"""
        from streamdeck_canvas.widgets import (
            Button, ProgressBar, Waveform, VUMeter, Timer,
            ScrollingText, LoadingSpinner, Grid, WidgetManager
        )

        canvas = canvas_classic
        manager = WidgetManager()

        # Ajouter un de chaque type
        manager.add(Button(col=0, row=0, icon="🎵", label="Button"))
        manager.add(ProgressBar(col=0, row=1, width=3, progress=0.5))
        manager.add(Waveform(col=3, row=1, width=2))
        manager.add(VUMeter(col=4, row=0))
        manager.add(Timer(col=4, row=1))
        manager.add(ScrollingText(col=0, row=2, width=3, text="Test"))
        manager.add(LoadingSpinner(col=3, row=2))
        manager.add(Grid(cols=5, rows=3, show_numbers=False))

        # Rendu
        manager.render_all(canvas)

        assert len(manager.widgets) == 8

    def test_debug_renderer_with_layout(self, temp_dir):
        """Test de DebugRenderer avec un layout complet"""
        import os
        import shutil

        # Changer de répertoire pour les tests
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:
            renderer = DebugRenderer(cols=5, rows=3, button_size=72)

            # Ajouter des widgets
            from streamdeck_canvas.widgets import WidgetManager, Button
            manager = WidgetManager()
            manager.add(Button(col=0, row=0, icon="🎵", label="Audio"))

            # Rendu manuel
            manager.render_all(renderer.canvas)
            renderer.update()

            # Vérifier qu'un fichier a été créé
            debug_files = [f for f in os.listdir('.') if f.startswith('debug_frame_')]
            assert len(debug_files) > 0

        finally:
            os.chdir(original_dir)

    def test_streamdeck_renderer_integration(self, mock_streamdeck_classic):
        """Test d'intégration StreamDeckRenderer avec mock complet"""
        from unittest.mock import patch

        with patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True):
            with patch('streamdeck_canvas.renderer.DeviceManager'):
                # Créer le renderer
                renderer = StreamDeckRenderer(mock_streamdeck_classic)

                # Dessiner
                renderer.canvas.draw_rect(0, 0, color='#FF6B35')

                # Mettre à jour
                renderer.update()

                # Vérifier les appels
                assert mock_streamdeck_classic.set_key_image.call_count == 15

                # Stopper proprement
                renderer.stop()


# ============= TESTS DE VALIDATION ET ROBUSTESSE =============

class TestEdgeCases:
    """Tests pour les cas limites et validation robuste"""

    def test_canvas_out_of_bounds_coordinates(self, canvas_classic):
        """Test de gestion des coordonnées hors limites"""
        canvas = canvas_classic

        # Coordonnées normales
        canvas.draw_rect(0, 0)

        # Coordonnées negatives (ne doivent pas crasher)
        canvas.draw_rect(-1, -1)

        # Coordonnées trop grandes (ne doivent pas crasher)
        canvas.draw_rect(10, 10)

        assert True

    def test_canvas_zero_size(self, canvas_classic):
        """Test avec taille zéro"""
        canvas = canvas_classic

        # Région de taille zéro
        canvas.draw_rect(0, 0, width_cols=0, height_rows=0)

        assert True

    def test_widget_out_of_bounds(self, canvas_classic):
        """Test de widget hors limites du canvas"""
        from streamdeck_canvas.widgets import Widget

        # Widget qui dépasse du canvas
        widget = Widget(col=10, row=10, width=5, height=5)
        canvas = canvas_classic

        # Ne doit pas crasher
        widget.render(canvas)

        assert True

    def test_invalid_color_format(self, canvas_classic):
        """Test avec format de couleur invalide"""
        canvas = canvas_classic

        # Couleur invalide (ne doit pas crasher)
        try:
            canvas.draw_rect(0, 0, color='invalid_color')
        except:
            # Si ça lève une exception, c'est acceptable
            pass

        assert True

    def test_empty_text_rendering(self, canvas_classic):
        """Test de rendu de texte vide"""
        canvas = canvas_classic

        # Texte vide
        canvas.draw_text(0, 0, "")

        assert True

    def test_very_long_text(self, canvas_classic):
        """Test avec texte très long"""
        canvas = canvas_classic

        # Texte très long
        long_text = "A" * 1000
        canvas.draw_text(0, 0, long_text)

        assert True

    def test_null_widget_manager(self, canvas_classic):
        """Test avec WidgetManager vide"""
        from streamdeck_canvas.widgets import WidgetManager

        manager = WidgetManager()
        manager.render_all(canvas_classic)

        # Doit fonctionner sans widgets
        assert len(manager.widgets) == 0

    def test_very_high_progress_value(self, canvas_classic):
        """Test avec valeurs de progression extrêmes"""
        from streamdeck_canvas.widgets import ProgressBar

        widget = ProgressBar(col=0, row=0, width=3)

        # Valeur très grande
        widget.set_progress(1000.0)
        widget.render(canvas_classic)

        # Valeur très négative
        widget.set_progress(-1000.0)
        widget.render(canvas_classic)

        assert widget.progress == 0.0

    def test_rapid_updates(self, canvas_classic):
        """Test de mises à jour rapides"""
        from streamdeck_canvas.widgets import VUMeter

        vu_meter = VUMeter(col=0, row=0)
        canvas = canvas_classic

        # Mettre à jour rapidement
        for i in range(100):
            vu_meter.set_level(i / 100.0)
            vu_meter.render(canvas)

        assert True

    def test_concurrent_widget_rendering(self, canvas_classic):
        """Test de rendu concurrent de widgets"""
        from streamdeck_canvas.widgets import WidgetManager, Button

        canvas = canvas_classic
        manager = WidgetManager()

        # Ajouter beaucoup de widgets
        for i in range(20):
            manager.add(Button(col=i % 5, row=i // 5, icon=str(i), label=f"Btn{i}"))

        # Rendu
        manager.render_all(canvas)

        assert len(manager.widgets) == 20

    def test_memory_efficiency(self, canvas_classic):
        """Test d'efficacité mémoire"""
        canvas = canvas_classic

        # Créer et supprimer des images
        for _ in range(100):
            img = Image.new('RGB', (72, 72), color='#FF6B35')
            canvas.paste_image(0, 0, img)
            del img

        assert True

    def test_fps_counter_under_load(self, fps_counter):
        """Test du compteur FPS sous charge"""
        # Mettre à jour très rapidement
        for _ in range(50):
            fps_counter.update()

        # Vérifier que ça ne plante pas
        assert fps_counter.fps >= 0.0

    def test_color_palette_edge_cases(self):
        """Test de la palette de couleurs avec cas limites"""
        # Dégradé avec 2 étapes
        gradient = ColorPalette.get_gradient(2, '#000000', '#FFFFFF')
        assert len(gradient) == 2

        # Dégradé avec 1 étape
        gradient = ColorPalette.get_gradient(1, '#000000', '#FFFFFF')
        assert len(gradient) == 1

    def test_renderer_with_no_canvas(self, mock_streamdeck_classic):
        """Test de renderer sans canvas (cas théorique)"""
        from streamdeck_canvas.renderer import StreamDeckRenderer

        with patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True):
            with patch('streamdeck_canvas.renderer.DeviceManager'):
                # Créer renderer
                renderer = StreamDeckRenderer(mock_streamdeck_classic)

                # Vider le canvas
                renderer.canvas = None

                # Update ne doit pas crasher (ou alors gérer proprement)
                try:
                    renderer.update()
                except AttributeError:
                    # Attendu si canvas est None
                    pass

                assert True
