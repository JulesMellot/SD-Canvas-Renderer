"""
Tests pour la détection et gestion des Stream Decks
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from streamdeck_canvas.utils import (
    StreamDeckManager,
    connect_stream_deck,
    scan_stream_decks,
    FPSCounter,
    Timer as UtilTimerClass,
    hex_to_rgb,
    rgb_to_hex,
    clamp,
    lerp,
    ease_in_out_cubic,
    ease_out_elastic,
    format_time,
    format_bytes,
    calculate_fps,
    create_rounded_mask,
    apply_rounded_corners,
    load_icon,
    measure_text_size,
    truncate_text,
    ColorPalette,
)


# ============= TESTS STREAM DECK MANAGER =============

class TestStreamDeckManager:
    """Tests pour StreamDeckManager"""

    @patch('streamdeck_canvas.utils.StreamDeckManager._init_library')
    def test_manager_init_with_library(self, mock_init):
        """Test d'initialisation avec librairie StreamDeck disponible"""
        # Simuler que DeviceManager est disponible
        mock_init.return_value = None

        # Créer manager après le patch
        manager = StreamDeckManager()
        manager.streamdecks_available = True
        manager.device_manager = Mock()

        assert manager.streamdecks_available == True
        assert manager.streamdecks == []

    @patch('streamdeck_canvas.utils.DeviceManager', side_effect=ImportError)
    def test_manager_init_without_library(self, mock_device_manager):
        """Test d'initialisation sans librairie StreamDeck"""
        manager = StreamDeckManager()

        assert manager.streamdecks_available == False
        assert manager.device_manager is None

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_detect_devices_no_device(self, mock_device_manager):
        """Test de détection sans device"""
        mock_device_manager.return_value.enumerate.return_value = []

        manager = StreamDeckManager()
        devices = manager.detect_devices()

        assert devices == []
        assert len(manager.streamdecks) == 0

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_detect_devices_single_classic(self, mock_device_manager, mock_streamdeck_classic):
        """Test de détection d'un Stream Deck Classic"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        devices = manager.detect_devices()

        assert len(devices) == 1
        assert devices[0]['index'] == 0
        assert devices[0]['deck_type'] == 'Stream Deck'
        assert devices[0]['serial'] == 'TEST123'
        assert devices[0]['cols'] == 5
        assert devices[0]['rows'] == 3
        assert devices[0]['button_size'] == 72
        assert devices[0]['total_keys'] == 15
        assert devices[0]['canvas_size'] == (360, 216)
        assert devices[0]['is_visual'] == True

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_detect_devices_multiple(self, mock_device_manager, mock_streamdeck_classic, mock_streamdeck_mini):
        """Test de détection de plusieurs devices"""
        mock_device_manager.return_value.enumerate.return_value = [
            mock_streamdeck_classic,
            mock_streamdeck_mini
        ]

        manager = StreamDeckManager()
        devices = manager.detect_devices()

        assert len(devices) == 2
        assert devices[0]['deck_type'] == 'Stream Deck'
        assert devices[1]['deck_type'] == 'Stream Deck Mini'

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_detect_devices_with_error(self, mock_device_manager, mock_streamdeck_classic):
        """Test de détection avec erreur sur un device"""
        # Le premier device lève une erreur
        mock_streamdeck_classic.open.side_effect = Exception("Device error")

        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        devices = manager.detect_devices()

        # Ne doit pas crash et retourner une liste vide
        assert devices == []

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_print_devices_info_no_devices(self, mock_device_manager, capsys):
        """Test d'affichage sans devices"""
        mock_device_manager.return_value.enumerate.return_value = []

        manager = StreamDeckManager()
        manager.print_devices_info()

        captured = capsys.readouterr()
        assert "Aucun Stream Deck trouvé" in captured.out
        assert "Dépannage" in captured.out

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_print_devices_info_single_device(self, mock_device_manager, mock_streamdeck_classic, capsys):
        """Test d'affichage avec un device"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        manager.print_devices_info()

        captured = capsys.readouterr()
        assert "Stream Deck #1" in captured.out
        assert "Stream Deck" in captured.out
        assert "Debug:" in captured.out
        assert "Réel:" in captured.out

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_connect_first_device_success(self, mock_device_manager, mock_streamdeck_classic):
        """Test de connexion au premier device (succès)"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_first_device(reset_deck=False)

        assert device is not None
        assert device['deck'] == mock_streamdeck_classic
        mock_streamdeck_classic.open.assert_called_once()

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_connect_first_device_no_devices(self, mock_device_manager):
        """Test de connexion sans devices"""
        mock_device_manager.return_value.enumerate.return_value = []

        manager = StreamDeckManager()
        device = manager.connect_first_device(reset_deck=False)

        assert device is None

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_connect_first_device_error(self, mock_device_manager, mock_streamdeck_classic):
        """Test de connexion avec erreur"""
        mock_streamdeck_classic.open.side_effect = Exception("Connection error")
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_first_device(reset_deck=False)

        assert device is None

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_connect_device_by_index_success(self, mock_device_manager, mock_streamdeck_classic, mock_streamdeck_mini):
        """Test de connexion par index (succès)"""
        mock_device_manager.return_value.enumerate.return_value = [
            mock_streamdeck_classic,
            mock_streamdeck_mini
        ]

        manager = StreamDeckManager()
        device = manager.connect_device_by_index(1, reset_deck=False)

        assert device is not None
        assert device['index'] == 1
        assert device['deck_type'] == 'Stream Deck Mini'

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_connect_device_by_index_invalid(self, mock_device_manager, mock_streamdeck_classic):
        """Test de connexion par index invalide"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_device_by_index(5, reset_deck=False)

        assert device is None

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_connect_device_by_index_negative(self, mock_device_manager, mock_streamdeck_classic):
        """Test de connexion avec index négatif"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_device_by_index(-1, reset_deck=False)

        assert device is None

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_connect_device_by_serial_success(self, mock_device_manager, mock_streamdeck_classic):
        """Test de connexion par numéro de série (succès)"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_device_by_serial('TEST123', reset_deck=False)

        assert device is not None
        assert device['serial'] == 'TEST123'

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_connect_device_by_serial_not_found(self, mock_device_manager, mock_streamdeck_classic):
        """Test de connexion par numéro de série inexistant"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_device_by_serial('NOTFOUND', reset_deck=False)

        assert device is None

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_create_renderer_debug_mode(self, mock_device_manager, mock_streamdeck_classic):
        """Test de création de renderer en mode debug"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        renderer = manager.create_renderer(debug_mode=True)

        assert renderer is not None
        from streamdeck_canvas.renderer import DebugRenderer
        assert isinstance(renderer, DebugRenderer)

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_create_renderer_real_device(self, mock_device_manager, mock_streamdeck_classic):
        """Test de création de renderer avec device réel"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_first_device(reset_deck=False)
        renderer = manager.create_renderer(device)

        assert renderer is not None
        from streamdeck_canvas.renderer import StreamDeckRenderer
        assert isinstance(renderer, StreamDeckRenderer)

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_create_renderer_no_device_info(self, mock_device_manager, mock_streamdeck_classic):
        """Test de création de renderer sans infos device (défaut)"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        renderer = manager.create_renderer(device_info=None, debug_mode=True)

        assert renderer is not None
        # Devrait utiliser les dimensions par défaut
        assert renderer.cols == 5
        assert renderer.rows == 3

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_close_device(self, mock_device_manager, mock_streamdeck_classic):
        """Test de fermeture de device"""
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_first_device(reset_deck=False)

        manager.close_device(device)

        mock_streamdeck_classic.reset.assert_called_once()
        mock_streamdeck_classic.set_brightness.assert_called_once_with(50)
        mock_streamdeck_classic.close.assert_called_once()

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_close_device_error(self, mock_device_manager, mock_streamdeck_classic):
        """Test de fermeture de device avec erreur"""
        mock_streamdeck_classic.reset.side_effect = Exception("Reset error")
        mock_device_manager.return_value.enumerate.return_value = [mock_streamdeck_classic]

        manager = StreamDeckManager()
        device = manager.connect_first_device(reset_deck=False)

        # Ne doit pas lever d'exception
        manager.close_device(device)

    @patch('streamdeck_canvas.utils.DeviceManager')
    def test_close_all_devices(self, mock_device_manager, mock_streamdeck_classic, mock_streamdeck_mini):
        """Test de fermeture de tous les devices"""
        mock_device_manager.return_value.enumerate.return_value = [
            mock_streamdeck_classic,
            mock_streamdeck_mini
        ]

        manager = StreamDeckManager()
        devices = manager.detect_devices()

        assert len(devices) == 2

        manager.close_all_devices()

        # Vérifier que tous ont été fermés
        assert mock_streamdeck_classic.close.call_count == 1
        assert mock_streamdeck_mini.close.call_count == 1
        assert len(manager.streamdecks) == 0


# ============= TESTS FONCTIONS UTILITAIRES =============

class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires"""

    def test_connect_stream_deck_function(self, mock_streamdeck_classic):
        """Test de la fonction connect_stream_deck"""
        with patch('streamdeck_canvas.utils.StreamDeckManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.connect_device_by_index.return_value = {'deck': mock_streamdeck_classic}
            mock_manager.create_renderer.return_value = Mock()

            result = connect_stream_deck(index=0)

            mock_manager.connect_device_by_index.assert_called_once_with(0)
            mock_manager.create_renderer.assert_called_once()

    def test_connect_stream_deck_debug_mode(self, mock_streamdeck_classic):
        """Test de connect_stream_deck en mode debug"""
        with patch('streamdeck_canvas.utils.StreamDeckManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.create_renderer.return_value = Mock()

            result = connect_stream_deck(debug_mode=True)

            mock_manager.create_renderer.assert_called_once_with(debug_mode=True)

    def test_scan_stream_decks_function(self, mock_streamdeck_classic):
        """Test de la fonction scan_stream_decks"""
        with patch('streamdeck_canvas.utils.StreamDeckManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.detect_devices.return_value = [mock_streamdeck_classic]
            mock_manager.print_devices_info = Mock()

            result = scan_stream_decks()

            mock_manager.detect_devices.assert_called_once()
            mock_manager.print_devices_info.assert_called_once()

    def test_calculate_fps(self):
        """Test de calculate_fps"""
        frame_times = [0.1, 0.1, 0.1, 0.1, 0.1]  # 10 FPS
        fps = calculate_fps(frame_times)

        assert abs(fps - 10.0) < 0.1

    def test_calculate_fps_empty(self):
        """Test de calculate_fps avec liste vide"""
        fps = calculate_fps([])

        assert fps == 0.0

    def test_calculate_fps_single_frame(self):
        """Test de calculate_fps avec un seul frame"""
        fps = calculate_fps([0.1])

        assert fps == 10.0

    def test_calculate_fps_window_size(self):
        """Test de calculate_fps avec fenêtre personnalisée"""
        # 50 frames mais fenêtre de 10
        frame_times = [0.1] * 50
        fps = calculate_fps(frame_times, window_size=10)

        assert fps > 0

    def test_create_rounded_mask(self):
        """Test de création de masque arrondi"""
        mask = create_rounded_mask((100, 100), radius=20)

        assert mask.size == (100, 100)
        assert mask.mode == 'L'

    def test_create_rounded_mask_large_radius(self):
        """Test de masque avec rayon trop grand"""
        mask = create_rounded_mask((100, 100), radius=100)

        # Le rayon doit être clampé
        assert mask.size == (100, 100)

    def test_apply_rounded_corners(self, sample_image):
        """Test d'application de coins arrondis"""
        img = sample_image.copy()
        img_rounded = apply_rounded_corners(img, radius=10)

        assert img_rounded.mode == 'RGBA'

    def test_apply_rounded_corners_already_rgba(self, sample_image_with_alpha):
        """Test avec image déjà RGBA"""
        img_rounded = apply_rounded_corners(sample_image_with_alpha, radius=10)

        assert img_rounded.mode == 'RGBA'

    def test_load_icon_success(self, temp_dir):
        """Test de chargement d'icône avec succès"""
        from PIL import Image

        # Créer une icône de test
        icon_path = f"{temp_dir}/test_icon.png"
        img = Image.new('RGB', (32, 32), color='#FF6B35')
        img.save(icon_path)

        loaded_icon = load_icon(icon_path)

        assert loaded_icon is not None

    def test_load_icon_resize(self, temp_dir):
        """Test de chargement avec redimensionnement"""
        from PIL import Image

        icon_path = f"{temp_dir}/test_icon.png"
        img = Image.new('RGB', (100, 100), color='#FF6B35')
        img.save(icon_path)

        loaded_icon = load_icon(icon_path, size=(32, 32))

        assert loaded_icon.size == (32, 32)

    def test_load_icon_not_found(self):
        """Test de chargement d'icône inexistante"""
        with pytest.raises(FileNotFoundError):
            load_icon('/path/does/not/exist.png')

    def test_measure_text_size(self):
        """Test de mesure de texte"""
        from streamdeck_canvas.canvas import StreamDeckCanvas

        canvas = StreamDeckCanvas(cols=5, rows=3)
        font = canvas.fonts['normal']

        width, height = measure_text_size("Test", font)

        assert width > 0
        assert height > 0

    def test_truncate_text_short(self):
        """Test de troncature avec texte déjà court"""
        from streamdeck_canvas.canvas import StreamDeckCanvas

        canvas = StreamDeckCanvas(cols=5, rows=3)
        font = canvas.fonts['normal']

        result = truncate_text("Short", font, max_width=100)

        assert result == "Short"

    def test_truncate_text_long(self):
        """Test de troncature avec texte long"""
        from streamdeck_canvas.canvas import StreamDeckCanvas

        canvas = StreamDeckCanvas(cols=5, rows=3)
        font = canvas.fonts['normal']

        long_text = "A" * 1000
        result = truncate_text(long_text, font, max_width=100)

        assert len(result) < len(long_text)
        assert result.endswith("...")


# ============= TESTS COLOR PALETTE =============

class TestColorPalette:
    """Tests pour ColorPalette"""

    def test_color_palette_all_colors(self):
        """Test de toutes les couleurs prédéfinies"""
        colors = [
            ColorPalette.PRIMARY,
            ColorPalette.SECONDARY,
            ColorPalette.ACCENT,
            ColorPalette.BACKGROUND,
            ColorPalette.SURFACE,
            ColorPalette.TEXT_PRIMARY,
            ColorPalette.TEXT_SECONDARY,
            ColorPalette.SUCCESS,
            ColorPalette.WARNING,
            ColorPalette.ERROR,
            ColorPalette.INFO,
            ColorPalette.AUDIO_LOW,
            ColorPalette.AUDIO_MID,
            ColorPalette.AUDIO_HIGH,
            ColorPalette.AUDIO_PEAK,
        ]

        # Vérifier que toutes sont des couleurs hex valides
        for color in colors:
            assert color.startswith('#')
            assert len(color) == 7
            # Vérifier que c'est convertible
            rgb = hex_to_rgb(color)
            assert len(rgb) == 3
            assert all(0 <= c <= 255 for c in rgb)

    def test_color_palette_get_gradient_default(self):
        """Test de génération de dégradé (paramètres par défaut)"""
        gradient = ColorPalette.get_gradient(5, '#000000', '#FFFFFF')

        assert len(gradient) == 5
        assert gradient[0] == '#000000'
        assert gradient[4] == '#FFFFFF'

    def test_color_palette_get_gradient_two_colors(self):
        """Test de dégradé avec deux couleurs"""
        gradient = ColorPalette.get_gradient(2, '#FF0000', '#0000FF')

        assert len(gradient) == 2
        assert gradient[0] == '#FF0000'
        assert gradient[1] == '#0000FF'

    def test_color_palette_get_gradient_single_color(self):
        """Test de dégradé avec une seule couleur"""
        gradient = ColorPalette.get_gradient(1, '#FF0000', '#0000FF')

        assert len(gradient) == 1
        assert gradient[0] == '#FF0000'  # Première couleur

    def test_color_palette_get_gradient_many_steps(self):
        """Test de dégradé avec beaucoup d'étapes"""
        gradient = ColorPalette.get_gradient(100, '#000000', '#FFFFFF')

        assert len(gradient) == 100


# ============= TESTS EDGE CASES ET ROBUSTESSE =============

class TestUtilityEdgeCases:
    """Tests de robustesse pour les utilitaires"""

    def test_hex_to_rgb_malformed(self):
        """Test avec couleur hex malformée"""
        with pytest.raises(ValueError):
            hex_to_rgb('#FFF')  # Trop court

        with pytest.raises(ValueError):
            hex_to_rgb('#FFFFFFF')  # Trop long

        with pytest.raises(ValueError):
            hex_to_rgb('#GGGGGG')  # Caractères invalides

    def test_rgb_to_hex_edge_cases(self):
        """Test rgb_to_hex avec valeurs extrêmes"""
        # Valeurs limites
        assert rgb_to_hex(0, 0, 0) == '#000000'
        assert rgb_to_hex(255, 255, 255) == '#FFFFFF'

    def test_rgb_to_hex_invalid_values(self):
        """Test rgb_to_hex avec valeurs invalides"""
        with pytest.raises(ValueError):
            rgb_to_hex(-1, 0, 0)  # Négatif

        with pytest.raises(ValueError):
            rgb_to_hex(256, 0, 0)  # Trop grand

    def test_interpolate_color_edge_cases(self):
        """Test interpolation aux extrêmes"""
        # Factor extrêmes (doivent être clampés)
        color = interpolate_color('#000000', '#FFFFFF', -10)
        assert color == '#000000'

        color = interpolate_color('#000000', '#FFFFFF', 10)
        assert color == '#FFFFFF'

    def test_clamp_edge_cases(self):
        """Test clamp avec cas extrêmes"""
        assert clamp(-100, 0, 100) == 0
        assert clamp(200, 0, 100) == 100
        assert clamp(50, 0, 100) == 50

    def test_lerp_edge_cases(self):
        """Test lerp avec facteurs extrêmes"""
        assert lerp(0, 100, -1) == 0
        assert lerp(0, 100, 2) == 100
        assert lerp(0, 100, 0.5) == 50

    def test_easing_functions_edge_cases(self):
        """Test des fonctions d'easing aux limites"""
        # ease_in_out_cubic
        assert ease_in_out_cubic(-1) == 0
        assert ease_in_out_cubic(2) == 1

        # ease_out_elastic
        assert ease_out_elastic(-1) == 0
        assert ease_out_elastic(2) == 1

    def test_format_time_edge_cases(self):
        """Test format_time avec valeurs extrêmes"""
        # Temps négatif
        result = format_time(-10)
        assert result == "00:00"

        # Temps très grand
        result = format_time(999999)
        assert "99" in result  # Heures

    def test_format_bytes_edge_cases(self):
        """Test format_bytes avec valeurs extrêmes"""
        assert format_bytes(-1) == "0 B"  # Négatif => 0
        assert format_bytes(0) == "0 B"

    def test_calculate_fps_edge_cases(self):
        """Test calculate_fps avec cas extrêmes"""
        # Liste vide
        assert calculate_fps([]) == 0

        # Temps nul
        assert calculate_fps([0]) == 0

    def test_fps_counter_edge_cases(self, fps_counter):
        """Test FPSCounter avec cas extrêmes"""
        # Update sans sleep (temps nul)
        for _ in range(10):
            fps_counter.update()

        # Ne doit pas planter
        assert fps_counter.fps >= 0

    def test_timer_edge_cases(self, timer):
        """Test Timer avec cas extrêmes"""
        # Elapsed sans start
        elapsed = timer.elapsed()
        assert elapsed == 0.0

        elapsed_ms = timer.elapsed_ms()
        assert elapsed_ms == 0.0

        # Stop sans start
        timer.stop()
        assert timer.end_time is None

    def test_create_rounded_mask_edge_cases(self):
        """Test create_rounded_mask avec tailles extrêmes"""
        # Taille très petite
        mask = create_rounded_mask((1, 1), radius=10)
        assert mask.size == (1, 1)

        # Taille nulle
        mask = create_rounded_mask((0, 0), radius=0)
        assert mask.size == (0, 0)

    def test_load_icon_edge_cases(self, temp_dir):
        """Test load_icon avec cas extrêmes"""
        # Fichier existant mais illisible
        bad_file = f"{temp_dir}/bad.png"
        with open(bad_file, 'w') as f:
            f.write("not an image")

        with pytest.raises(Exception):
            load_icon(bad_file)
