"""
Validateurs pour Stream Deck Canvas Renderer

Fournit des fonctions de validation robustes pour tous les paramètres,
avec des messages d'erreur clairs et une gestion d'erreurs centralisée.
"""

from typing import Tuple, Union, Optional, Any
import re
from .exceptions import (
    InvalidParameterError,
    ParameterRangeError,
    MissingParameterError,
    InvalidButtonCoordinatesError,
    InvalidCanvasSizeError,
    ColorError,
    WidgetSizeError,
    WidgetOutOfBoundsError,
    FrameRateError,
    InvalidOrientationError,
)


# ============= VALIDATION GÉNÉRALE =============

def validate_not_none(value: Any, param_name: str) -> None:
    """Valide qu'un paramètre n'est pas None"""
    if value is None:
        raise MissingParameterError(f"Le paramètre '{param_name}' ne peut pas être None")


def validate_type(value: Any, expected_type: type, param_name: str) -> None:
    """Valide le type d'un paramètre"""
    if not isinstance(value, expected_type):
        raise InvalidParameterError(
            f"Le paramètre '{param_name}' doit être de type {expected_type.__name__}, "
            f"reçu: {type(value).__name__}"
        )


def validate_in_range(
    value: Union[int, float],
    min_val: Union[int, float],
    max_val: Union[int, float],
    param_name: str
) -> None:
    """Valide qu'une valeur est dans une plage donnée"""
    if not isinstance(value, (int, float)):
        raise InvalidParameterError(f"Le paramètre '{param_name}' doit être numérique")

    if value < min_val or value > max_val:
        raise ParameterRangeError(
            f"Le paramètre '{param_name}' doit être entre {min_val} et {max_val}, "
            f"reçu: {value}"
        )


def validate_positive(value: Union[int, float], param_name: str) -> None:
    """Valide qu'une valeur est positive"""
    if not isinstance(value, (int, float)):
        raise InvalidParameterError(f"Le paramètre '{param_name}' doit être numérique")

    if value < 0:
        raise ParameterRangeError(
            f"Le paramètre '{param_name}' doit être positif, reçu: {value}"
        )


def validate_positive_nonzero(value: Union[int, float], param_name: str) -> None:
    """Valide qu'une valeur est positive et non nulle"""
    if not isinstance(value, (int, float)):
        raise InvalidParameterError(f"Le paramètre '{param_name}' doit être numérique")

    if value <= 0:
        raise ParameterRangeError(
            f"Le paramètre '{param_name}' doit être > 0, reçu: {value}"
        )


# ============= VALIDATION CANVAS =============

def validate_canvas_size(cols: int, rows: int, button_size: int) -> None:
    """Valide les paramètres de taille du canvas"""
    # Validation des types
    validate_type(cols, int, 'cols')
    validate_type(rows, int, 'rows')
    validate_type(button_size, int, 'button_size')

    # Validation des valeurs
    validate_positive_nonzero(cols, 'cols')
    validate_positive_nonzero(rows, 'rows')
    validate_positive_nonzero(button_size, 'button_size')

    # Tailles acceptées pour button_size
    if button_size not in (72, 80, 96):
        raise InvalidCanvasSizeError(
            f"button_size doit être 72, 80 ou 96 pixels, reçu: {button_size}"
        )

    # Limites maximales raisonnables
    if cols > 16 or rows > 16:
        raise InvalidCanvasSizeError(
            f"Canvas trop grand: {cols}×{rows}. Maximum recommandé: 16×16"
        )


def validate_button_coordinates(
    canvas_cols: int,
    canvas_rows: int,
    col: int,
    row: int,
    width: int = 1,
    height: int = 1
) -> None:
    """Valide les coordonnées d'un bouton ou d'une région"""
    # Types
    validate_type(canvas_cols, int, 'canvas_cols')
    validate_type(canvas_rows, int, 'canvas_rows')
    validate_type(col, int, 'col')
    validate_type(row, int, 'row')
    validate_type(width, int, 'width')
    validate_type(height, int, 'height')

    # Plages
    if not 0 <= col < canvas_cols:
        raise InvalidButtonCoordinatesError(
            f"Colonne {col} hors limites (0 à {canvas_cols-1})"
        )

    if not 0 <= row < canvas_rows:
        raise InvalidButtonCoordinatesError(
            f"Rangée {row} hors limites (0 à {canvas_rows-1})"
        )

    # Taille
    validate_positive_nonzero(width, 'width')
    validate_positive_nonzero(height, 'height')

    # Limites étendues
    if col + width > canvas_cols:
        raise InvalidButtonCoordinatesError(
            f"Région déborde à droite: col={col}, width={width}, "
            f"canvas_cols={canvas_cols}"
        )

    if row + height > canvas_rows:
        raise InvalidButtonCoordinatesError(
            f"Région déborde en bas: row={row}, height={row}, "
            f"canvas_rows={canvas_rows}"
        )


def validate_region_coordinates(
    canvas_cols: int,
    canvas_rows: int,
    start_col: int,
    start_row: int,
    width_cols: int,
    height_rows: int
) -> None:
    """Valide les coordonnées d'une région"""
    validate_button_coordinates(
        canvas_cols, canvas_rows,
        start_col, start_row,
        width_cols, height_rows
    )


# ============= VALIDATION COULEURS =============

def validate_color(color: str) -> None:
    """Valide un format de couleur hexadécimale"""
    validate_type(color, str, 'color')

    # Accepter avec ou sans #
    color_str = color.lstrip('#')

    # Vérifier le format (6 caractères hexadécimaux)
    if len(color_str) != 6:
        raise ColorError(
            f"Couleur doit être au format #RRGGBB, reçu: {color} (longueur: {len(color_str)})"
        )

    # Vérifier que c'est de l'hexadécimal
    if not re.match(r'^[0-9A-Fa-f]{6}$', color_str):
        raise ColorError(
            f"Couleur doit contenir uniquement des caractères hexadécimaux, reçu: {color}"
        )


def validate_optional_color(color: Optional[str]) -> None:
    """Valide une couleur optionnelle (peut être None)"""
    if color is not None:
        validate_color(color)


# ============= VALIDATION WIDGETS =============

def validate_widget_size(width: int, height: int) -> None:
    """Valide la taille d'un widget"""
    validate_type(width, int, 'width')
    validate_type(height, int, 'height')
    validate_positive_nonzero(width, 'width')
    validate_positive_nonzero(height, 'height')

    if width > 16 or height > 16:
        raise WidgetSizeError(
            f"Widget trop grand: {width}×{height}. Maximum recommandé: 16×16"
        )


def validate_widget_bounds(
    canvas_cols: int,
    canvas_rows: int,
    col: int,
    row: int,
    width: int,
    height: int
) -> None:
    """Valide qu'un widget reste dans les limites du canvas"""
    if col < 0 or row < 0:
        raise WidgetOutOfBoundsError(
            f"Position de widget invalide: col={col}, row={row} (doivent être >= 0)"
        )

    if col + width > canvas_cols:
        raise WidgetOutOfBoundsError(
            f"Widget déborde à droite: col={col}+width={width} > canvas_cols={canvas_cols}"
        )

    if row + height > canvas_rows:
        raise WidgetOutOfBoundsError(
            f"Widget déborde en bas: row={row}+height={height} > canvas_rows={canvas_rows}"
        )


# ============= VALIDATION RENDERER =============

def validate_orientation(orientation: str) -> None:
    """Valide l'orientation du renderer"""
    valid_orientations = {
        'normal',
        'rotated',
        'h_mirror',
        'v_mirror',
        'h_mirror_rotated',
        'v_mirror_rotated'
    }

    validate_type(orientation, str, 'orientation')

    if orientation not in valid_orientations:
        raise InvalidOrientationError(
            f"Orientation invalide: '{orientation}'. "
            f"Valeurs acceptées: {', '.join(sorted(valid_orientations))}"
        )


def validate_framerate(fps: int) -> None:
    """Valide le framerate"""
    validate_type(fps, int, 'fps')
    validate_positive(fps, 'fps')

    if fps > 60:
        raise FrameRateError(
            f"FPS trop élevé: {fps}. Maximum recommandé: 60 FPS"
        )

    if fps < 1:
        raise FrameRateError(
            f"FPS trop faible: {fps}. Minimum: 1 FPS"
        )


# ============= VALIDATION DESSIN =============

def validate_draw_rect_params(
    col: int, row: int,
    width_cols: int, height_rows: int,
    border_width: int, radius: int
) -> None:
    """Valide les paramètres de draw_rect"""
    validate_positive_nonzero(col, 'col')
    validate_positive_nonzero(row, 'row')
    validate_positive_nonzero(width_cols, 'width_cols')
    validate_positive_nonzero(height_rows, 'height_rows')
    validate_positive_nonzero(border_width, 'border_width')
    validate_positive_nonzero(radius, 'radius')

    # Radius ne doit pas dépasser la moitié de la plus petite dimension
    min_dimension = min(width_cols, height_rows)
    if radius > min_dimension:
        raise InvalidParameterError(
            f"Radius {radius} trop grand pour la région {width_cols}×{height_rows}"
        )


def validate_text_params(text: str, size: str, align: str) -> None:
    """Valide les paramètres de texte"""
    validate_type(text, str, 'text')
    validate_type(size, str, 'size')
    validate_type(align, str, 'align')

    valid_sizes = {'huge', 'large', 'title', 'normal', 'small', 'tiny'}
    if size not in valid_sizes:
        raise InvalidParameterError(
            f"Taille de police invalide: '{size}'. "
            f"Valeurs acceptées: {', '.join(sorted(valid_sizes))}"
        )

    valid_aligns = {'center', 'top', 'bottom', 'left'}
    if align not in valid_aligns:
        raise InvalidParameterError(
            f"Alignement invalide: '{align}'. "
            f"Valeurs acceptées: {', '.join(sorted(valid_aligns))}"
        )


def validate_circle_params(col: int, row: int, radius: int) -> None:
    """Valide les paramètres de cercle"""
    validate_positive_nonzero(col, 'col')
    validate_positive_nonzero(row, 'row')
    validate_positive_nonzero(radius, 'radius')

    # Radius ne doit pas dépasser la taille du bouton
    if radius > 50:  # Taille maximale raisonnable pour un cercle
        raise InvalidParameterError(
            f"Radius {radius} trop grand. Maximum recommandé: 50"
        )


# ============= VALIDATION CACHE/PERFORMANCE =============

def validate_cache_size(size: int) -> None:
    """Valide la taille du cache"""
    validate_type(size, int, 'cache_size')
    validate_positive_nonzero(size, 'cache_size')

    if size > 10000:
        raise InvalidParameterError(
            f"Taille de cache trop grande: {size}. Maximum: 10000"
        )


# ============= DÉCORATEURS DE VALIDATION =============

def validated(func):
    """
    Décorateur pour valider automatiquement les paramètres
    Usage: Place @validated avant une fonction qui utilise les validateurs ci-dessus
    """
    import inspect

    def wrapper(*args, **kwargs):
        # Note: Pour une implémentation complète, analyser les annotations
        # et les types attendus pour valider automatiquement
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ============= FONCTIONS DE CONVERSION SÉCURISÉES =============

def safe_hex_to_rgb(color: str) -> Tuple[int, int, int]:
    """
    Convertit une couleur hex en RGB avec validation
    Plus robuste que l'implémentation directe
    """
    validate_color(color)
    color_str = color.lstrip('#')

    try:
        return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))
    except ValueError as e:
        raise ColorError(f"Impossible de convertir la couleur: {color}") from e


def safe_clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limite une valeur entre min et max avec validation
    """
    if min_val >= max_val:
        raise InvalidParameterError(
            f"min_val ({min_val}) doit être < max_val ({max_val})"
        )

    return max(min_val, min(max_val, value))
