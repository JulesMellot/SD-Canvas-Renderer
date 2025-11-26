"""
Canvas unifié pour Stream Deck

Version refactorisée avec:
- API robuste avec validation complète
- Gestion d'erreurs centralisée
- Optimisations de performance (cache, lazy loading)
- Types hints complets
- Backward compatibility
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, List, Optional, Dict, Union, Any
import math
import re
from functools import lru_cache

from .exceptions import (
    CanvasError,
    CanvasNotInitializedError,
    InvalidCanvasSizeError,
    InvalidButtonCoordinatesError,
    ColorError,
    DrawingError,
    FontError,
    InvalidParameterError,
)
from .validators import (
    validate_canvas_size,
    validate_button_coordinates,
    validate_color,
    validate_optional_color,
    validate_positive_nonzero,
    validate_type,
    safe_hex_to_rgb,
    safe_clamp,
)


class StreamDeckCanvas:
    """
    Canvas unifié pour Stream Deck

    Représente la surface complète du Stream Deck comme un seul canvas.
    Coordonnées en (col, row) de boutons.

    Optimisations:
    - Cache des conversions de couleurs (LRU cache)
    - Lazy loading des polices
    - Validation complète des paramètres
    - Gestion d'erreurs robuste
    """

    # Tailles standard des Stream Decks
    STREAM_DECK_SIZES = {
        'classic': (5, 3, 72),
        'mini': (3, 2, 80),
        'xl': (8, 4, 96),
    }

    # Tailles de polices prédéfinies
    FONT_SIZES = {
        'huge': 32,
        'large': 24,
        'title': 18,
        'normal': 14,
        'small': 11,
        'tiny': 9
    }

    # Chemins de polices par OS
    FONT_PATHS = [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        "Arial.ttf",  # Fallback
    ]

    def __init__(
        self,
        cols: int = 5,
        rows: int = 3,
        button_size: int = 72,
        background_color: str = '#000000'
    ):
        """
        Initialise le canvas

        Args:
            cols: Nombre de colonnes (défaut: 5 pour Stream Deck Classic)
            rows: Nombre de rangées (défaut: 3)
            button_size: Taille en pixels d'un bouton (72, 80, ou 96)
            background_color: Couleur de fond par défaut (#000000)

        Raises:
            InvalidCanvasSizeError: Si les dimensions sont invalides
            ColorError: Si la couleur de fond est invalide
        """
        # Validation des paramètres
        validate_canvas_size(cols, rows, button_size)
        validate_color(background_color)

        # Attributs principaux
        self.cols = cols
        self.rows = rows
        self.button_size = button_size

        # Dimensions du canvas
        self.width = cols * button_size
        self.height = rows * button_size

        # Canvas PIL (initialisé dans clear())
        self.image: Optional[Image.Image] = None
        self.draw: Optional[ImageDraw.Draw] = None

        # Polices (lazy loading)
        self._fonts: Optional[Dict[str, ImageFont.ImageFont]] = None
        self._fonts_loaded = False

        # Cache pour les couleurs (optimisation)
        self._color_cache: Dict[str, Tuple[int, int, int]] = {}

        # Initialiser le canvas
        self.clear(background_color)

    # ============= PROPRIÉTÉS =============

    @property
    def is_initialized(self) -> bool:
        """Vérifie si le canvas est initialisé"""
        return self.image is not None and self.draw is not None

    @property
    def fonts(self) -> Dict[str, ImageFont.ImageFont]:
        """Retourne le dictionnaire des polices (lazy loading)"""
        if not self._fonts_loaded:
            self._load_fonts()
        return self._fonts

    # ============= GESTION DU CANVAS =============

    def clear(self, color: str = '#000000') -> None:
        """
        Efface le canvas avec une couleur

        Args:
            color: Couleur de fond (#000000 par défaut)

        Raises:
            ColorError: Si la couleur est invalide
            CanvasError: Si erreur lors de la création du canvas
        """
        validate_color(color)

        try:
            rgb = self._hex_to_rgb(color)
            self.image = Image.new('RGB', (self.width, self.height), color=rgb)
            self.draw = ImageDraw.Draw(self.image)
        except Exception as e:
            raise CanvasError(f"Erreur lors du clear du canvas: {e}") from e

    # ============= CONVERSION COULEURS =============

    @staticmethod
    @lru_cache(maxsize=128)
    def hex_to_rgb_cached(color: str) -> Tuple[int, int, int]:
        """
        Convertit hex en RGB avec cache LRU

        Args:
            color: Couleur au format #RRGGBB ou RRGGBB

        Returns:
            Tuple (r, g, b) avec valeurs 0-255

        Raises:
            ColorError: Si la couleur est invalide
        """
        validate_color(color)
        color_str = color.lstrip('#')

        try:
            return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))
        except ValueError as e:
            raise ColorError(f"Couleur invalide: {color}") from e

    def hex_to_rgb(self, color: str) -> Tuple[int, int, int]:
        """
        API publique pour conversion couleur hex vers RGB

        Utilise un cache interne pour les conversions répétitives.

        Args:
            color: Couleur au format #RRGGBB ou RRGGBB

        Returns:
            Tuple (r, g, b)

        Raises:
            ColorError: Si la couleur est invalide

        Examples:
            >>> canvas = StreamDeckCanvas()
            >>> canvas.hex_to_rgb('#FF6B35')
            (255, 107, 53)
        """
        validate_color(color)

        # Utiliser le cache si disponible
        if color in self._color_cache:
            return self._color_cache[color]

        # Calculer et mettre en cache
        rgb = self.hex_to_rgb_cached(color)
        self._color_cache[color] = rgb
        return rgb

    def _hex_to_rgb(self, color: str) -> Tuple[int, int, int]:
        """
        Méthode privée pour backward compatibility
        Dépréciée: utilisez hex_to_rgb() à la place

        Args:
            color: Couleur hex

        Returns:
            Tuple RGB
        """
        return self.hex_to_rgb(color)

    # ============= GÉOMÉTRIE =============

    def get_button_rect(self, col: int, row: int) -> Tuple[int, int, int, int]:
        """
        Retourne (x, y, width, height) d'un bouton

        Args:
            col: Colonne du bouton
            row: Rangée du bouton

        Returns:
            Tuple (x, y, width, height) en pixels

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
        """
        validate_button_coordinates(self.cols, self.rows, col, row)

        x = col * self.button_size
        y = row * self.button_size
        return (x, y, self.button_size, self.button_size)

    def get_region_rect(
        self,
        start_col: int,
        start_row: int,
        width_cols: int,
        height_rows: int
    ) -> Tuple[int, int, int, int]:
        """
        Retourne (x, y, width, height) d'une région de boutons

        Args:
            start_col: Colonne de départ
            start_row: Rangée de départ
            width_cols: Largeur en nombre de boutons
            height_rows: Hauteur en nombre de boutons

        Returns:
            Tuple (x, y, width, height) en pixels

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
        """
        validate_button_coordinates(
            self.cols, self.rows,
            start_col, start_row,
            width_cols, height_rows
        )

        x = start_col * self.button_size
        y = start_row * self.button_size
        w = width_cols * self.button_size
        h = height_rows * self.button_size
        return (x, y, w, h)

    # ============= PRIMITIVES DE DESSIN =============

    def draw_rect(
        self,
        col: int,
        row: int,
        width_cols: int = 1,
        height_rows: int = 1,
        color: str = '#FFFFFF',
        border: Optional[str] = None,
        border_width: int = 2,
        radius: int = 0
    ) -> None:
        """
        Dessine un rectangle

        Args:
            col: Colonne de départ
            row: Rangée de départ
            width_cols: Largeur en boutons (défaut: 1)
            height_rows: Hauteur en boutons (défaut: 1)
            color: Couleur de fond (#FFFFFF)
            border: Couleur de bordure (None = pas de bordure)
            border_width: Épaisseur de bordure (défaut: 2)
            radius: Rayon des coins arrondis (défaut: 0 = rectangle droit)

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
            ColorError: Si couleur invalide
            DrawingError: Si erreur de dessin
        """
        # Validation
        validate_button_coordinates(
            self.cols, self.rows,
            col, row, width_cols, height_rows
        )
        validate_color(color)
        validate_optional_color(border)
        validate_positive_nonzero(border_width, 'border_width')

        # Radius peut être 0 (rectangle droit) ou > 0 (coins arrondis)
        validate_type(radius, int, 'radius')
        if radius < 0:
            raise ParameterRangeError(f"radius doit être >= 0, reçu: {radius}")

        # Vérifier que le canvas est initialisé
        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            x, y, w, h = self.get_region_rect(col, row, width_cols, height_rows)

            rgb_fill = self.hex_to_rgb(color)
            rgb_border = self.hex_to_rgb(border) if border else None

            padding = 3

            # Utiliser rounded_rectangle si radius > 0
            if radius > 0:
                self.draw.rounded_rectangle(
                    [x + padding, y + padding, x + w - padding, y + h - padding],
                    radius=radius,
                    fill=rgb_fill,
                    outline=rgb_border,
                    width=border_width if border else 0
                )
            else:
                self.draw.rectangle(
                    [x + padding, y + padding, x + w - padding, y + h - padding],
                    fill=rgb_fill,
                    outline=rgb_border,
                    width=border_width if border else 0
                )
        except Exception as e:
            raise DrawingError(f"Erreur lors du dessin du rectangle: {e}") from e

    def draw_gradient_rect(
        self,
        col: int,
        row: int,
        width_cols: int,
        height_rows: int,
        color_start: str,
        color_end: str,
        direction: str = 'vertical'
    ) -> None:
        """
        Dessine un rectangle avec un dégradé linéaire

        Args:
            col: Colonne de départ
            row: Rangée de départ
            width_cols: Largeur en boutons
            height_rows: Hauteur en boutons
            color_start: Couleur de début (hex)
            color_end: Couleur de fin (hex)
            direction: 'vertical' ou 'horizontal'

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
            ColorError: Si couleur invalide
            DrawingError: Si erreur de dessin
        """
        validate_button_coordinates(
            self.cols, self.rows,
            col, row, width_cols, height_rows
        )
        validate_color(color_start)
        validate_color(color_end)

        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            x, y, w, h = self.get_region_rect(col, row, width_cols, height_rows)
            
            # Ajouter un petit padding comme pour les rects normaux
            padding = 3
            draw_x = x + padding
            draw_y = y + padding
            draw_w = w - 2 * padding
            draw_h = h - 2 * padding

            # Créer l'image du dégradé
            base = Image.new('RGB', (draw_w, draw_h), color_start)
            top = Image.new('RGB', (draw_w, draw_h), color_end)
            mask = Image.new('L', (draw_w, draw_h))
            mask_data = []

            for y_p in range(draw_h):
                for x_p in range(draw_w):
                    if direction == 'vertical':
                        p = int(255 * (y_p / draw_h))
                    else:
                        p = int(255 * (x_p / draw_w))
                    mask_data.append(p)

            mask.putdata(mask_data)
            base.paste(top, (0, 0), mask)

            # Coller sur le canvas
            self.image.paste(base, (draw_x, draw_y))

        except Exception as e:
            raise DrawingError(f"Erreur lors du dessin du dégradé: {e}") from e

    def draw_rounded_rect(
        self,
        col: int,
        row: int,
        width_cols: int = 1,
        height_rows: int = 1,
        color: str = '#FFFFFF',
        border: Optional[str] = None,
        border_width: int = 2,
        radius: int = 10
    ) -> None:
        """
        Dessine un rectangle avec coins arrondis

        Args:
            col: Colonne de départ
            row: Rangée de départ
            width_cols: Largeur en boutons
            height_rows: Hauteur en boutons
            color: Couleur de fond
            border: Couleur de bordure
            border_width: Épaisseur de bordure
            radius: Rayon des coins (défaut: 10)

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
            ColorError: Si couleur invalide
            DrawingError: Si erreur de dessin
        """
        # Déléguer à draw_rect avec radius
        self.draw_rect(
            col, row,
            width_cols, height_rows,
            color, border, border_width,
            radius=max(1, radius)  # Radius minimum de 1
        )

    def draw_text(
        self,
        col: int,
        row: int,
        text: str,
        color: str = '#FFFFFF',
        size: str = 'normal',
        align: str = 'center',
        offset_x: int = 0,
        offset_y: int = 0
    ) -> None:
        """
        Dessine du texte

        Args:
            col: Colonne du bouton
            row: Rangée du bouton
            text: Texte à dessiner
            color: Couleur du texte
            size: Taille de police ('huge', 'large', 'title', 'normal', 'small', 'tiny')
            align: Alignement ('center', 'top', 'bottom', 'left')
            offset_x: Décalage horizontal en pixels
            offset_y: Décalage vertical en pixels

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
            ColorError: Si couleur invalide
            FontError: Si taille de police invalide
            DrawingError: Si erreur de dessin
        """
        # Validation
        validate_button_coordinates(self.cols, self.rows, col, row)
        validate_type(text, str, 'text')
        validate_color(color)

        if size not in self.FONT_SIZES:
            raise FontError(
                f"Taille de police invalide: '{size}'. "
                f"Valeurs acceptées: {', '.join(self.FONT_SIZES.keys())}"
            )

        if align not in ('center', 'top', 'bottom', 'left'):
            raise InvalidParameterError(
                f"Alignement invalide: '{align}'. "
                f"Valeurs acceptées: center, top, bottom, left"
            )

        # Vérifier canvas initialisé
        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            x, y, w, h = self.get_button_rect(col, row)
            font = self.fonts[size]

            # Calculer position selon alignement
            if align == 'center':
                text_x = x + w // 2 + offset_x
                text_y = y + h // 2 + offset_y
                anchor = "mm"
            elif align == 'top':
                text_x = x + w // 2 + offset_x
                text_y = y + 10 + offset_y
                anchor = "mt"
            elif align == 'bottom':
                text_x = x + w // 2 + offset_x
                text_y = y + h - 10 + offset_y
                anchor = "mb"
            else:  # left
                text_x = x + offset_x
                text_y = y + h // 2 + offset_y
                anchor = "lm"

            rgb = self.hex_to_rgb(color)
            self.draw.text(
                (text_x, text_y),
                text,
                font=font,
                fill=rgb,
                anchor=anchor,
                align='center'
            )
        except Exception as e:
            raise DrawingError(f"Erreur lors du dessin du texte: {e}") from e

    def text_at_pos(
        self,
        x: int,
        y: int,
        text: str,
        color: str = '#FFFFFF',
        size: str = 'normal',
        anchor: str = 'mm'
    ) -> None:
        """
        Dessine du texte à une position en pixels

        Args:
            x: Position X en pixels
            y: Position Y en pixels
            text: Texte à dessiner
            color: Couleur du texte
            size: Taille de police
            anchor: Ancrage ('mm', 'mt', 'mb', 'lm', 'rm', 'tl', 'tr', 'bl', 'br')

        Raises:
            ColorError: Si couleur invalide
            FontError: Si taille invalide
            DrawingError: Si erreur de dessin
        """
        validate_type(x, int, 'x')
        validate_type(y, int, 'y')
        validate_type(text, str, 'text')
        validate_color(color)

        if size not in self.FONT_SIZES:
            raise FontError(f"Taille de police invalide: '{size}'")

        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            font = self.fonts[size]
            rgb = self.hex_to_rgb(color)
            self.draw.text(
                (x, y),
                text,
                font=font,
                fill=rgb,
                anchor=anchor
            )
        except Exception as e:
            raise DrawingError(f"Erreur lors du dessin du texte: {e}") from e

    def draw_icon_text(
        self,
        col: int,
        row: int,
        icon: str,
        label: str,
        icon_color: str = '#FFFFFF',
        label_color: str = '#FFFFFF',
        icon_size: str = 'large',
        label_size: str = 'small'
    ) -> None:
        """
        Dessine une icône avec un label en dessous (pattern classique)

        Args:
            col: Colonne du bouton
            row: Rangée du bouton
            icon: Texte de l'icône
            label: Texte du label
            icon_color: Couleur de l'icône
            label_color: Couleur du label
            icon_size: Taille de police pour l'icône
            label_size: Taille de police pour le label

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
            ColorError: Si couleur invalide
            FontError: Si taille invalide
        """
        # Icône en haut
        self.draw_text(
            col, row,
            icon,
            color=icon_color,
            size=icon_size,
            align='center',
            offset_y=-10
        )

        # Label en bas
        self.draw_text(
            col, row,
            label,
            color=label_color,
            size=label_size,
            align='center',
            offset_y=20
        )

    def draw_circle(
        self,
        col: int,
        row: int,
        radius: int,
        color: str = '#FFFFFF',
        border: Optional[str] = None,
        border_width: int = 2
    ) -> None:
        """
        Dessine un cercle centré sur un bouton

        Args:
            col: Colonne du bouton
            row: Rangée du bouton
            radius: Rayon du cercle en pixels
            color: Couleur de remplissage
            border: Couleur de bordure (None = pas de bordure)
            border_width: Épaisseur de bordure

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
            ColorError: Si couleur invalide
            InvalidParameterError: Si radius invalide
            DrawingError: Si erreur de dessin
        """
        validate_button_coordinates(self.cols, self.rows, col, row)
        validate_positive_nonzero(radius, 'radius')
        validate_color(color)
        validate_optional_color(border)
        validate_positive_nonzero(border_width, 'border_width')

        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            x, y, w, h = self.get_button_rect(col, row)
            center_x = x + w // 2
            center_y = y + h // 2

            # Vérifier que le cercle tient dans le bouton
            max_radius = min(w, h) // 2 - 5
            radius = safe_clamp(radius, 1, max_radius)

            rgb_fill = self.hex_to_rgb(color)
            rgb_border = self.hex_to_rgb(border) if border else None

            self.draw.ellipse(
                [center_x - radius, center_y - radius,
                 center_x + radius, center_y + radius],
                fill=rgb_fill,
                outline=rgb_border,
                width=border_width if border else 0
            )
        except Exception as e:
            raise DrawingError(f"Erreur lors du dessin du cercle: {e}") from e

    def draw_arc(
        self,
        col: int,
        row: int,
        radius: int,
        start_angle: int,
        end_angle: int,
        color: str = '#FFFFFF',
        width: int = 2
    ) -> None:
        """
        Dessine un arc de cercle

        Args:
            col: Colonne du centre
            row: Rangée du centre
            radius: Rayon
            start_angle: Angle de début en degrés (0 = droite, 90 = bas)
            end_angle: Angle de fin en degrés
            color: Couleur du trait
            width: Épaisseur du trait

        Raises:
            DrawingError: Si erreur de dessin
        """
        validate_button_coordinates(self.cols, self.rows, col, row)
        validate_positive_nonzero(radius, 'radius')
        validate_color(color)
        validate_positive_nonzero(width, 'width')

        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            x, y, w, h = self.get_button_rect(col, row)
            center_x = x + w // 2
            center_y = y + h // 2

            rgb_color = self.hex_to_rgb(color)

            self.draw.arc(
                [center_x - radius, center_y - radius,
                 center_x + radius, center_y + radius],
                start=start_angle,
                end=end_angle,
                fill=rgb_color,
                width=width
            )
        except Exception as e:
            raise DrawingError(f"Erreur lors du dessin de l'arc: {e}") from e

    def draw_pieslice(
        self,
        col: int,
        row: int,
        radius: int,
        start_angle: int,
        end_angle: int,
        color: str = '#FFFFFF',
        border: Optional[str] = None,
        border_width: int = 2
    ) -> None:
        """
        Dessine une part de tarte (secteur angulaire)

        Args:
            col: Colonne du centre
            row: Rangée du centre
            radius: Rayon
            start_angle: Angle de début
            end_angle: Angle de fin
            color: Couleur de remplissage
            border: Couleur de bordure
            border_width: Épaisseur de bordure

        Raises:
            DrawingError: Si erreur de dessin
        """
        validate_button_coordinates(self.cols, self.rows, col, row)
        validate_positive_nonzero(radius, 'radius')
        validate_color(color)
        validate_optional_color(border)

        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            x, y, w, h = self.get_button_rect(col, row)
            center_x = x + w // 2
            center_y = y + h // 2

            rgb_fill = self.hex_to_rgb(color)
            rgb_border = self.hex_to_rgb(border) if border else None

            self.draw.pieslice(
                [center_x - radius, center_y - radius,
                 center_x + radius, center_y + radius],
                start=start_angle,
                end=end_angle,
                fill=rgb_fill,
                outline=rgb_border,
                width=border_width if border else 0
            )
        except Exception as e:
            raise DrawingError(f"Erreur lors du dessin du pieslice: {e}") from e

    def draw_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str = '#FFFFFF',
        width: int = 2
    ) -> None:
        """
        Dessine une ligne (coordonnées en pixels)

        Args:
            x1, y1: Point de départ
            x2, y2: Point d'arrivée
            color: Couleur de la ligne
            width: Épaisseur de la ligne

        Raises:
            ColorError: Si couleur invalide
            DrawingError: Si erreur de dessin
        """
        validate_type(x1, int, 'x1')
        validate_type(y1, int, 'y1')
        validate_type(x2, int, 'x2')
        validate_type(y2, int, 'y2')
        validate_color(color)
        validate_positive_nonzero(width, 'width')

        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            rgb = self.hex_to_rgb(color)
            self.draw.line([(x1, y1), (x2, y2)], fill=rgb, width=width)
        except Exception as e:
            raise DrawingError(f"Erreur lors du dessin de la ligne: {e}") from e

    # ============= GESTION DES TILES =============

    def get_tiles(self) -> List[Image.Image]:
        """
        Découpe le canvas en tiles individuelles pour chaque bouton

        L'ordre correspond à celui du Stream Deck (key 0 à 14)

        Returns:
            Liste d'images PIL (une par bouton)

        Raises:
            CanvasNotInitializedError: Si canvas non initialisé
        """
        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        tiles = []

        # Parcourir en ordre inverse (de bas en haut) pour correspondre au Stream Deck
        for row in reversed(range(self.rows)):
            for col in range(self.cols):
                x = col * self.button_size
                y = row * self.button_size
                tile = self.image.crop((
                    x, y,
                    x + self.button_size,
                    y + self.button_size
                ))
                tiles.append(tile)

        return tiles

    # ============= UTILITAIRES =============

    def save_debug(self, filename: str = "debug_canvas.png") -> None:
        """
        Sauvegarde le canvas pour debug

        Args:
            filename: Nom du fichier de sortie

        Raises:
            CanvasNotInitializedError: Si canvas non initialisé
            DrawingError: Si erreur de sauvegarde
        """
        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            self.image.save(filename)
        except Exception as e:
            raise DrawingError(f"Erreur lors de la sauvegarde: {e}") from e

    def paste_image(self, col: int, row: int, image: Image.Image) -> None:
        """
        Colle une image PIL sur le canvas

        Args:
            col: Colonne du bouton
            row: Rangée du bouton
            image: Image PIL à coller

        Raises:
            InvalidButtonCoordinatesError: Si coordonnées invalides
            InvalidParameterError: Si image invalide
            CanvasNotInitializedError: Si canvas non initialisé
            DrawingError: Si erreur de collage
        """
        validate_button_coordinates(self.cols, self.rows, col, row)
        validate_type(image, Image.Image, 'image')

        if not self.is_initialized:
            raise CanvasNotInitializedError("Canvas non initialisé")

        try:
            x, y, _, _ = self.get_button_rect(col, row)

            # Redimensionner l'image si nécessaire
            if image.size != (self.button_size, self.button_size):
                image = image.resize(
                    (self.button_size, self.button_size),
                    Image.Resampling.LANCZOS
                )

            self.image.paste(image, (x, y))
        except Exception as e:
            raise DrawingError(f"Erreur lors du collage d'image: {e}") from e

    # ============= POLICES (LAZY LOADING) =============

    def _load_fonts(self) -> None:
        """
        Charge les polices système (lazy loading)

        Raises:
            FontError: Si erreur de chargement des polices
        """
        if self._fonts_loaded:
            return

        try:
            self._fonts = {}

            for size_name, size_px in self.FONT_SIZES.items():
                loaded = False

                for font_path in self.FONT_PATHS:
                    try:
                        self._fonts[size_name] = ImageFont.truetype(font_path, size_px)
                        loaded = True
                        break
                    except (IOError, OSError):
                        # Police suivante
                        continue

                if not loaded:
                    # Fallback: police par défaut
                    self._fonts[size_name] = ImageFont.load_default()

            self._fonts_loaded = True

        except Exception as e:
            raise FontError(f"Erreur lors du chargement des polices: {e}") from e

    def reload_fonts(self) -> None:
        """
        Recharge les polices (utile après installation d'une nouvelle police)

        Raises:
            FontError: Si erreur de rechargement
        """
        self._fonts_loaded = False
        self._fonts = None
        self._load_fonts()

    # ============= CACHE MANAGEMENT =============

    def clear_cache(self) -> None:
        """Vide le cache des couleurs"""
        self._color_cache.clear()

    def get_cache_info(self) -> Dict[str, int]:
        """
        Retourne les informations du cache

        Returns:
            Dictionnaire avec les stats du cache
        """
        return {
            'color_cache_size': len(self._color_cache),
            'color_cache_maxsize': 128,
            'fonts_loaded': self._fonts_loaded,
        }

    # ============= COMPARISON & REPR =============

    def __repr__(self) -> str:
        return f"StreamDeckCanvas(cols={self.cols}, rows={self.rows}, size={self.button_size}px)"

    def __eq__(self, other) -> bool:
        if not isinstance(other, StreamDeckCanvas):
            return False
        return (
            self.cols == other.cols and
            self.rows == other.rows and
            self.button_size == other.button_size
        )
