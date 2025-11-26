"""
Exceptions personnalisées pour Stream Deck Canvas Renderer

Toutes les exceptions du système dérivent de StreamDeckCanvasError
pour une gestion d'erreur centralisée et robuste.
"""


class StreamDeckCanvasError(Exception):
    """Classe de base pour toutes les exceptions du projet"""
    pass


# ============= ERREURS CANVAS =============

class CanvasError(StreamDeckCanvasError):
    """Erreur générale du canvas"""
    pass


class InvalidCanvasSizeError(CanvasError):
    """Taille de canvas invalide"""
    pass


class InvalidButtonCoordinatesError(CanvasError):
    """Coordonnées de bouton invalides"""
    pass


class CanvasNotInitializedError(CanvasError):
    """Canvas non initialisé"""
    pass


class ColorError(CanvasError):
    """Erreur de couleur invalide"""
    pass


class DrawingError(CanvasError):
    """Erreur lors du dessin"""
    pass


class FontError(CanvasError):
    """Erreur de police"""
    pass


# ============= ERREURS WIDGETS =============

class WidgetError(StreamDeckCanvasError):
    """Erreur générale des widgets"""
    pass


class WidgetOutOfBoundsError(WidgetError):
    """Widget en dehors des limites du canvas"""
    pass


class WidgetSizeError(WidgetError):
    """Taille de widget invalide"""
    pass


class InvalidWidgetTypeError(WidgetError):
    """Type de widget invalide"""
    pass


class WidgetRenderError(WidgetError):
    """Erreur lors du rendu du widget"""
    pass


# ============= ERREURS RENDERER =============

class RendererError(StreamDeckCanvasError):
    """Erreur générale du renderer"""
    pass


class DeviceNotConnectedError(RendererError):
    """Appareil non connecté"""
    pass


class DeviceDisconnectedError(RendererError):
    """Appareil déconnecté en cours d'utilisation"""
    pass


class RenderingError(RendererError):
    """Erreur lors du rendu"""
    pass


class InvalidOrientationError(RendererError):
    """Orientation invalide"""
    pass


class FrameRateError(RendererError):
    """Framerate invalide"""
    pass


class DebugModeError(RendererError):
    """Erreur spécifique au mode debug"""
    pass


# ============= ERREURS HARDWARE =============

class HardwareError(StreamDeckCanvasError):
    """Erreur générale hardware"""
    pass


class DeviceNotFoundError(HardwareError):
    """Appareil Stream Deck non trouvé"""
    pass


class DevicePermissionError(HardwareError):
    """Permissions insuffisantes pour accéder à l'appareil"""
    pass


class DeviceConfigError(HardwareError):
    """Configuration de l'appareil invalide"""
    pass


class ImageConversionError(HardwareError):
    """Erreur de conversion d'image"""
    pass


# ============= ERREURS VALIDATION =============

class ValidationError(StreamDeckCanvasError):
    """Erreur de validation des paramètres"""
    pass


class InvalidParameterError(ValidationError):
    """Paramètre invalide"""
    pass


class MissingParameterError(ValidationError):
    """Paramètre manquant"""
    pass


class ParameterRangeError(ValidationError):
    """Paramètre hors limites"""
    pass
