"""
Configuration et fixtures communes pour les tests
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch
from PIL import Image


# ============= FIXTURES DE BASE =============

@pytest.fixture
def temp_dir():
    """Répertoire temporaire pour les tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_image():
    """Image PIL d'exemple pour les tests"""
    img = Image.new('RGB', (100, 100), color='#FF6B35')
    return img


@pytest.fixture
def sample_image_with_alpha():
    """Image PIL avec transparence"""
    img = Image.new('RGBA', (100, 100), color=(255, 107, 53, 128))
    return img


# ============= FIXTURES STREAM DECK =============

@pytest.fixture
def mock_streamdeck_classic():
    """Mock d'un Stream Deck Classic (5×3, 72px)"""
    mock = Mock()
    mock.key_count.return_value = 15
    mock.key_image_format.return_value = {'size': (72, 72), 'format': 'JPEG'}
    mock.deck_type.return_value = "Stream Deck"
    mock.get_serial_number.return_value = "TEST123"
    mock.get_firmware_version.return_value = "1.00"
    mock.key_layout.return_value = (5, 3)
    mock.set_brightness = Mock()
    mock.set_key_callback = Mock()
    mock.set_key_image = Mock()
    mock.reset = Mock()
    mock.open = Mock()
    mock.close = Mock()
    mock.is_visual.return_value = True
    mock.is_touch.return_value = False
    return mock


@pytest.fixture
def mock_streamdeck_mini():
    """Mock d'un Stream Deck Mini (3×2, 80px)"""
    mock = Mock()
    mock.key_count.return_value = 6
    mock.key_image_format.return_value = {'size': (80, 80), 'format': 'JPEG'}
    mock.deck_type.return_value = "Stream Deck Mini"
    mock.get_serial_number.return_value = "MINI456"
    mock.get_firmware_version.return_value = "1.00"
    mock.key_layout.return_value = (3, 2)
    mock.set_brightness = Mock()
    mock.set_key_callback = Mock()
    mock.set_key_image = Mock()
    mock.reset = Mock()
    mock.open = Mock()
    mock.close = Mock()
    mock.is_visual.return_value = True
    mock.is_touch.return_value = False
    return mock


@pytest.fixture
def mock_streamdeck_xl():
    """Mock d'un Stream Deck XL (8×4, 96px)"""
    mock = Mock()
    mock.key_count.return_value = 32
    mock.key_image_format.return_value = {'size': (96, 96), 'format': 'JPEG'}
    mock.deck_type.return_value = "Stream Deck XL"
    mock.get_serial_number.return_value = "XL789"
    mock.get_firmware_version.return_value = "1.00"
    mock.key_layout.return_value = (8, 4)
    mock.set_brightness = Mock()
    mock.set_key_callback = Mock()
    mock.set_key_image = Mock()
    mock.reset = Mock()
    mock.open = Mock()
    mock.close = Mock()
    mock.is_visual.return_value = True
    mock.is_touch.return_value = True
    return mock


@pytest.fixture
def mock_device_manager():
    """Mock du DeviceManager StreamDeck"""
    with patch('streamdeck_canvas.renderer.DeviceManager') as mock_mgr:
        yield mock_mgr


@pytest.fixture
def device_manager_with_classic(mock_streamdeck_classic):
    """DeviceManager qui retourne un Stream Deck Classic"""
    with patch('streamdeck_canvas.utils.DeviceManager') as mock_mgr:
        mock_mgr.return_value.enumerate.return_value = [mock_streamdeck_classic]
        yield mock_mgr


# ============= FIXTURES CANVAS =============

@pytest.fixture
def canvas_classic():
    """Canvas pour Stream Deck Classic (5×3, 72px)"""
    from streamdeck_canvas.canvas import StreamDeckCanvas
    return StreamDeckCanvas(cols=5, rows=3, button_size=72)


@pytest.fixture
def canvas_mini():
    """Canvas pour Stream Deck Mini (3×2, 80px)"""
    from streamdeck_canvas.canvas import StreamDeckCanvas
    return StreamDeckCanvas(cols=3, rows=2, button_size=80)


@pytest.fixture
def canvas_xl():
    """Canvas pour Stream Deck XL (8×4, 96px)"""
    from streamdeck_canvas.canvas import StreamDeckCanvas
    return StreamDeckCanvas(cols=8, rows=4, button_size=96)


# ============= FIXTURES RENDERER =============

@pytest.fixture
def debug_renderer_classic():
    """DebugRenderer pour Stream Deck Classic"""
    from streamdeck_canvas.renderer import DebugRenderer
    return DebugRenderer(cols=5, rows=3, button_size=72)


@pytest.fixture
def debug_renderer_mini():
    """DebugRenderer pour Stream Deck Mini"""
    from streamdeck_canvas.renderer import DebugRenderer
    return DebugRenderer(cols=3, rows=2, button_size=80)


# ============= FIXTURES WIDGETS =============

@pytest.fixture
def button_widget():
    """Widget Button simple"""
    from streamdeck_canvas.widgets import Button
    return Button(col=0, row=0, icon="🎵", label="Audio")


@pytest.fixture
def progress_bar_widget():
    """Widget ProgressBar"""
    from streamdeck_canvas.widgets import ProgressBar
    return ProgressBar(col=0, row=0, width=3, progress=0.5)


@pytest.fixture
def waveform_widget():
    """Widget Waveform"""
    from streamdeck_canvas.widgets import Waveform
    return Waveform(col=0, row=0, width=5, progress=0.3)


@pytest.fixture
def vu_meter_widget():
    """Widget VUMeter"""
    from streamdeck_canvas.widgets import VUMeter
    return VUMeter(col=0, row=0, level=0.7)


@pytest.fixture
def timer_widget():
    """Widget Timer"""
    from streamdeck_canvas.widgets import Timer
    return Timer(col=0, row=0, current_time=120.0, total_time=300.0)


@pytest.fixture
def scrolling_text_widget():
    """Widget ScrollingText"""
    from streamdeck_canvas.widgets import ScrollingText
    return ScrollingText(col=0, row=0, width=3, text="Mon fichier très long.mp3")


@pytest.fixture
def loading_spinner_widget():
    """Widget LoadingSpinner"""
    from streamdeck_canvas.widgets import LoadingSpinner
    return LoadingSpinner(col=0, row=0)


@pytest.fixture
def grid_widget():
    """Widget Grid"""
    from streamdeck_canvas.widgets import Grid
    return Grid(cols=5, rows=3)


@pytest.fixture
def widget_manager():
    """WidgetManager avec widgets d'exemple"""
    from streamdeck_canvas.widgets import WidgetManager
    manager = WidgetManager()

    # Ajouter des widgets d'exemple
    manager.add(Button(col=0, row=0, icon="🎵", label="Audio"))
    manager.add(Button(col=1, row=0, icon="📹", label="Video"))
    manager.add(ProgressBar(col=0, row=1, width=5))

    return manager


# ============= FIXTURES UTILITAIRES =============

@pytest.fixture
def fps_counter():
    """Compteur FPS pour tests"""
    from streamdeck_canvas.utils import FPSCounter
    return FPSCounter()


@pytest.fixture
def timer():
    """Timer pour tests"""
    from streamdeck_canvas.utils import Timer
    return Timer()


# ============= FIXTURES COMPLEXES =============

@pytest.fixture
def streamdeck_renderer_classic(mock_streamdeck_classic):
    """StreamDeckRenderer complet avec mock"""
    from streamdeck_canvas.renderer import StreamDeckRenderer

    with patch('streamdeck_canvas.renderer.STREAMDECK_AVAILABLE', True):
        with patch('streamdeck_canvas.renderer.DeviceManager'):
            renderer = StreamDeckRenderer(mock_streamdeck_classic)
            yield renderer


@pytest.fixture
def complex_layout_canvas():
    """Canvas avec layout complexe pour tests d'intégration"""
    from streamdeck_canvas.canvas import StreamDeckCanvas
    from streamdeck_canvas.widgets import (
        Button, ProgressBar, VUMeter, Timer, WidgetManager
    )

    canvas = StreamDeckCanvas(cols=5, rows=3, button_size=72)
    manager = WidgetManager()

    # Ajouter plusieurs widgets
    manager.add(Button(col=0, row=0, icon="🎵", label="Music", bg_color='#FF6B35'))
    manager.add(Button(col=1, row=0, icon="📹", label="Video", bg_color='#4CAF50'))
    manager.add(Button(col=2, row=0, icon="🎮", label="Game", bg_color='#2196F3'))
    manager.add(ProgressBar(col=0, row=1, width=5, progress=0.65))
    manager.add(VUMeter(col=4, row=1, level=0.8))
    manager.add(Timer(col=0, row=2, current_time=150, total_time=300))

    return canvas, manager


# ============= HELPER FUNCTIONS =============

def assert_image_size(image, expected_width, expected_height):
    """Vérifie qu'une image a les dimensions attendues"""
    assert image.size == (expected_width, expected_height), \
        f"Image size {image.size} != ({expected_width}, {expected_height})"


def assert_image_mode(image, expected_mode):
    """Vérifie qu'une image a le mode attendu"""
    assert image.mode == expected_mode, \
        f"Image mode {image.mode} != {expected_mode}"


def assert_colors_match(color1, color2, tolerance=0):
    """Compare deux couleurs (hex ou RGB)"""
    if isinstance(color1, str):
        from streamdeck_canvas.utils import hex_to_rgb
        color1 = hex_to_rgb(color1)
    if isinstance(color2, str):
        from streamdeck_canvas.utils import hex_to_rgb
        color2 = hex_to_rgb(color2)

    for c1, c2 in zip(color1, color2):
        assert abs(c1 - c2) <= tolerance, \
            f"Colors don't match: {color1} vs {color2}"


def create_test_image(width, height, color='#FF0000'):
    """Crée une image de test avec une couleur donnée"""
    from streamdeck_canvas.utils import hex_to_rgb
    rgb = hex_to_rgb(color)
    return Image.new('RGB', (width, height), color=rgb)


# ============= MARKERS HELPERS =============

def pytest_configure(config):
    """Configuration personnalisée pour pytest"""
    config.addinivalue_line(
        "markers", "unit: Mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as integration test"
    )


@pytest.fixture(autouse=True)
def reset_imports():
    """Reset les modules importés entre les tests"""
    import sys
    modules_to_reset = [
        k for k in sys.modules.keys()
        if k.startswith('streamdeck_canvas')
    ]
    yield
    for module in modules_to_reset:
        if module in sys.modules:
            del sys.modules[module]
