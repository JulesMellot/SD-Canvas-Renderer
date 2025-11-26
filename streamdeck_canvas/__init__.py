"""
Stream Deck Canvas Renderer
A unified canvas rendering engine for Elgato Stream Deck

Version refactorisée avec:
- API robuste avec validation complète
- Gestion d'erreurs centralisée et exceptions personnalisées
- Optimisations de performance (cache, lazy loading)
- Interface abstraite propre pour les renderers
- Documentation complète et types hints
"""

__version__ = "1.0.0"

# Renderer layer
from .renderer import (
    RendererBase,
    StreamDeckRenderer,
    DebugRenderer,
    RendererCallbacks
)

# Application layer
from .app import StreamDeckApp

# Canvas layer
from .canvas import StreamDeckCanvas

# Widget system (Core)
from .widgets import (
    Widget,
    Button,
    ProgressBar,
    Waveform,
    VUMeter,
    Timer,
    ScrollingText,
    LoadingSpinner,
    Grid,
    WidgetManager
)

# Dev Framework
from .framework import SimpleWidget, functional_widget

# Advanced Widgets
from .widgets_chart import RadialGauge, LineGraph, PieChart
from .widgets_audio import SpectrumVisualizer, RotaryVolume
from .widgets_anim import MatrixRain, BreathingRect

# Utility functions
from .utils import (
    ColorPalette,
    FPSCounter,
    hex_to_rgb,
    rgb_to_hex,
    clamp,
    interpolate_color,
    format_time,
    format_bytes,
)

__all__ = [
    # App
    'StreamDeckApp',

    # Renderer
    'RendererBase',
    'StreamDeckRenderer',
    'DebugRenderer',

    # Canvas
    'StreamDeckCanvas',

    # Core Widgets
    'Widget',
    'SimpleWidget',
    'functional_widget',
    'Button',
    'ProgressBar',
    'Waveform',
    'VUMeter',
    'Timer',
    'ScrollingText',
    'LoadingSpinner',
    'Grid',
    'WidgetManager',

    # Advanced Widgets
    'RadialGauge',
    'LineGraph',
    'PieChart',
    'SpectrumVisualizer',
    'RotaryVolume',
    'MatrixRain',
    'BreathingRect',

    # Utilities
    'ColorPalette',
    'FPSCounter',
    'hex_to_rgb',
]
