"""
Widgets préconstruits pour Stream Deck Canvas

Version refactorisée avec:
- Validation complète des paramètres
- Gestion d'erreurs robuste
- Corrections des méthodes manquantes (rounded_rectangle, etc.)
- Utilisation de l'API canvas refactorisée
- Backward compatibility
- Documentation complète
"""

from PIL import Image, ImageDraw
from typing import List, Optional, Tuple, Dict, Any
import math
from abc import ABC, abstractmethod

from .canvas import StreamDeckCanvas
from .exceptions import (
    WidgetError,
    WidgetOutOfBoundsError,
    WidgetSizeError,
    WidgetRenderError,
    InvalidWidgetTypeError,
    InvalidParameterError,
)
from .validators import (
    validate_widget_size,
    validate_widget_bounds,
    validate_type,
    validate_positive_nonzero,
    validate_color,
    safe_clamp,
)


# ============= CLASSE DE BASE =============

class Widget(ABC):
    """
    Classe de base abstraite pour tous les widgets

    Un widget sait se dessiner sur un canvas à une position donnée
    """

    def __init__(
        self,
        col: int,
        row: int,
        width: int = 1,
        height: int = 1
    ):
        """
        Initialise le widget

        Args:
            col: Colonne de départ (0-based)
            row: Rangée de départ (0-based)
            width: Largeur en nombre de boutons (minimum: 1)
            height: Hauteur en nombre de boutons (minimum: 1)

        Raises:
            WidgetSizeError: Si taille invalide
        """
        # Validation
        validate_type(col, int, 'col')
        validate_type(row, int, 'row')
        validate_widget_size(width, height)

        self.col = col
        self.row = row
        self.width = width
        self.height = height
        self.visible = True

        # État du widget (pour animations, etc.)
        self._state: Dict[str, Any] = {}

    @abstractmethod
    def render(self, canvas: StreamDeckCanvas) -> None:
        """
        Rend le widget sur le canvas

        Args:
            canvas: Instance de StreamDeckCanvas

        Raises:
            WidgetRenderError: Si erreur de rendu
        """
        pass

    def is_point_inside(self, col: int, row: int) -> bool:
        """
        Vérifie si un point (col, row) est dans le widget

        Args:
            col: Colonne à vérifier
            row: Rangée à vérifier

        Returns:
            True si le point est dans le widget
        """
        validate_type(col, int, 'col')
        validate_type(row, int, 'row')

        return (self.col <= col < self.col + self.width and
                self.row <= row < self.row + self.height)

    def validate_bounds(self, canvas: StreamDeckCanvas) -> None:
        """
        Valide que le widget reste dans les limites du canvas

        Args:
            canvas: Canvas de référence

        Raises:
            WidgetOutOfBoundsError: Si widget déborde
        """
        validate_widget_bounds(
            canvas.cols, canvas.rows,
            self.col, self.row,
            self.width, self.height
        )

    def set_state(self, key: str, value: Any) -> None:
        """
        Définit un état interne du widget (pour animations, etc.)

        Args:
            key: Clé de l'état
            value: Valeur
        """
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Récupère un état interne du widget

        Args:
            key: Clé de l'état
            default: Valeur par défaut si clé inexistante

        Returns:
            Valeur de l'état
        """
        return self._state.get(key, default)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(col={self.col}, row={self.row}, size={self.width}×{self.height})"


# ============= WIDGETS PRÉCONSTRUITS =============

class Button(Widget):
    """
    Bouton simple avec icône et label

    Widget de base pour afficher un bouton avec texte (icône) et label
    """

    def __init__(
        self,
        col: int,
        row: int,
        icon: str,
        label: str,
        bg_color: str = '#4A4543',
        icon_color: str = '#FFF8F0',
        label_color: str = '#FFF8F0',
        border: bool = False,
        border_color: str = '#FFF8F0'
    ):
        """
        Initialise le bouton

        Args:
            col: Colonne
            row: Rangée
            icon: Texte de l'icône
            label: Texte du label
            bg_color: Couleur de fond
            icon_color: Couleur de l'icône
            label_color: Couleur du label
            border: Afficher une bordure
            border_color: Couleur de la bordure

        Raises:
            ColorError: Si couleur invalide
            InvalidParameterError: Si paramètres invalides
        """
        super().__init__(col, row, 1, 1)

        # Validation
        validate_type(icon, str, 'icon')
        validate_type(label, str, 'label')
        validate_color(bg_color)
        validate_color(icon_color)
        validate_color(label_color)
        validate_type(border, bool, 'border')
        validate_color(border_color)

        self.icon = icon
        self.label = label
        self.bg_color = bg_color
        self.icon_color = icon_color
        self.label_color = label_color
        self.border = border
        self.border_color = border_color
        self.pressed = False

    def render(self, canvas: StreamDeckCanvas) -> None:
        """
        Rend le bouton

        Raises:
            WidgetRenderError: Si erreur
        """
        if not self.visible:
            return

        try:
            self.validate_bounds(canvas)

            # Fond
            canvas.draw_rect(
                self.col, self.row,
                color=self.bg_color,
                border=self.border_color if self.border else None,
                border_width=2,
                radius=10
            )

            # Icône + Label (pattern classique)
            canvas.draw_icon_text(
                self.col, self.row,
                icon=self.icon,
                label=self.label,
                icon_color=self.icon_color,
                label_color=self.label_color
            )

            # Effet pressed (overlay transparent)
            if self.pressed:
                canvas.draw_rect(
                    self.col, self.row,
                    color='#00000088',
                    radius=10
                )

        except Exception as e:
            raise WidgetRenderError(f"Erreur lors du rendu du bouton: {e}") from e


class ProgressBar(Widget):
    """
    Barre de progression horizontale sur plusieurs boutons

    Affiche une progression de 0% à 100%
    """

    def __init__(
        self,
        col: int,
        row: int,
        width: int,
        progress: float = 0.0,
        bg_color: str = '#1A1110',
        fill_color: str = '#FF6B35',
        border_color: str = '#4A4543',
        show_percentage: bool = True
    ):
        """
        Initialise la barre de progression

        Args:
            col: Colonne de départ
            row: Rangée de départ
            width: Largeur en boutons
            progress: Progression (0.0 à 1.0)
            bg_color: Couleur de fond
            fill_color: Couleur de la barre
            border_color: Couleur de la bordure
            show_percentage: Afficher le pourcentage

        Raises:
            WidgetSizeError: Si largeur invalide
            ColorError: Si couleur invalide
            InvalidParameterError: Si progression invalide
        """
        super().__init__(col, row, width, 1)

        validate_widget_size(width, 1)
        validate_color(bg_color)
        validate_color(fill_color)
        validate_color(border_color)
        validate_type(show_percentage, bool, 'show_percentage')

        # Clamp progress
        self.progress = safe_clamp(progress, 0.0, 1.0)
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.show_percentage = show_percentage

    def set_progress(self, value: float) -> None:
        """
        Met à jour la progression (0.0 à 1.0)

        Args:
            value: Nouvelle progression

        Raises:
            InvalidParameterError: Si valeur invalide
        """
        validate_type(value, (int, float), 'value')
        self.progress = safe_clamp(float(value), 0.0, 1.0)

    def render(self, canvas: StreamDeckCanvas) -> None:
        """Rend la barre de progression"""
        if not self.visible:
            return

        try:
            self.validate_bounds(canvas)

            x, y, w, h = canvas.get_region_rect(self.col, self.row, self.width, self.height)

            # Dessiner le fond (utilise draw_rect avec padding)
            canvas.draw_rect(
                self.col, self.row,
                width_cols=self.width,
                height_rows=1,
                color=self.bg_color,
                border=self.border_color,
                border_width=2,
                radius=8
            )

            # Barre de progression (dessinée directement)
            padding = 10
            inner_x = x + padding
            inner_y = y + padding
            inner_w = w - 2 * padding
            inner_h = h - 2 * padding

            # Largeur de la barre selon progression
            bar_width = int(inner_w * self.progress)

            if bar_width > 0:
                # Utiliser rounded_rectangle via canvas.draw_rounded_rect
                canvas.draw_rounded_rect(
                    self.col, self.row,
                    width_cols=self.width,
                    height_rows=1,
                    color=self.fill_color,
                    radius=6
                )

            # Dessiner la barre de progression par-dessus
            if bar_width > 0:
                # Calculer en pixels pour la barre
                center_y = y + h // 2
                bar_x = inner_x
                bar_height = inner_h - 10

                # Utiliser draw.rectangle pour la barre elle-même
                canvas.draw.rectangle(
                    [bar_x, center_y - bar_height // 2,
                     bar_x + bar_width, center_y + bar_height // 2],
                    fill=canvas.hex_to_rgb(self.fill_color)
                )

            # Pourcentage
            if self.show_percentage:
                percentage_text = f"{int(self.progress * 100)}%"
                center_col = self.col + self.width // 2
                canvas.draw_text(
                    center_col, self.row,
                    text=percentage_text,
                    color='#FFF8F0',
                    size='normal',
                    align='center'
                )

        except Exception as e:
            raise WidgetRenderError(f"Erreur lors du rendu de ProgressBar: {e}") from e


class Waveform(Widget):
    """
    Visualisation de waveform audio animée

    Affiche une forme d'onde avec progression, cues et animation
    """

    def __init__(
        self,
        col: int,
        row: int,
        width: int,
        progress: float = 0.0,
        cues: Optional[List[float]] = None,
        bg_color: str = '#1A1110',
        played_color: str = '#FF6B35',
        unplayed_color: str = '#4A4543',
        cue_color: str = '#FFB627',
        position_color: str = '#F7931E'
    ):
        """
        Initialise la waveform

        Args:
            col: Colonne de départ
            row: Rangée de départ
            width: Largeur en boutons
            progress: Position actuelle (0.0 à 1.0)
            cues: Liste des positions de cue (0.0 à 1.0)
            bg_color: Couleur de fond
            played_color: Couleur de la partie jouée
            unplayed_color: Couleur de la partie non jouée
            cue_color: Couleur des cues
            position_color: Couleur de l'indicateur de position

        Raises:
            WidgetSizeError: Si largeur invalide
            ColorError: Si couleur invalide
        """
        super().__init__(col, row, width, 1)

        validate_widget_size(width, 1)
        validate_color(bg_color)
        validate_color(played_color)
        validate_color(unplayed_color)
        validate_color(cue_color)
        validate_color(position_color)

        # Clamp progress
        self.progress = safe_clamp(progress, 0.0, 1.0)
        self.cues = cues or []
        self.bg_color = bg_color
        self.played_color = played_color
        self.unplayed_color = unplayed_color
        self.cue_color = cue_color
        self.position_color = position_color

        # Animation
        self.animation_frame = 0

    def set_progress(self, value: float) -> None:
        """Met à jour la position (0.0 à 1.0)"""
        validate_type(value, (int, float), 'value')
        self.progress = safe_clamp(float(value), 0.0, 1.0)

    def add_cue(self, position: float) -> None:
        """Ajoute un cue marker"""
        validate_type(position, (int, float), 'position')
        position = safe_clamp(float(position), 0.0, 1.0)

        if position not in self.cues:
            self.cues.append(position)
            self.cues.sort()

    def clear_cues(self) -> None:
        """Efface tous les cues"""
        self.cues.clear()

    def render(self, canvas: StreamDeckCanvas) -> None:
        """Rend la waveform"""
        if not self.visible:
            return

        try:
            self.validate_bounds(canvas)

            x, y, w, h = canvas.get_region_rect(self.col, self.row, self.width, self.height)

            # Fond
            canvas.draw.rectangle(
                [x, y, x + w, y + h],
                fill=canvas.hex_to_rgb(self.bg_color)
            )

            center_y = y + h // 2
            progress_x = x + int(w * self.progress)

            # Dessiner la waveform (sinusoïde stylisée)
            for i in range(0, w, 3):
                px = x + i

                # Hauteur de la vague avec animation
                wave_height = int(18 * abs(math.sin(i * 0.08 + self.animation_frame * 0.15)))

                # Couleur selon si c'est joué ou non
                if px < progress_x:
                    color = canvas.hex_to_rgb(self.played_color)
                    line_width = 2
                else:
                    color = canvas.hex_to_rgb(self.unplayed_color)
                    line_width = 1

                # Ligne verticale
                canvas.draw.line(
                    [(px, center_y - wave_height), (px, center_y + wave_height)],
                    fill=color,
                    width=line_width
                )

            # Dessiner les cues
            for cue_pos in self.cues:
                cue_x = x + int(w * cue_pos)
                # Petit losange
                canvas.draw.polygon(
                    [(cue_x, center_y - 8), (cue_x + 4, center_y),
                     (cue_x, center_y + 8), (cue_x - 4, center_y)],
                    fill=canvas.hex_to_rgb(self.cue_color)
                )

            # Position actuelle (gros losange)
            canvas.draw.polygon(
                [(progress_x, center_y - 12), (progress_x + 6, center_y),
                 (progress_x, center_y + 12), (progress_x - 6, center_y)],
                fill=canvas.hex_to_rgb(self.position_color),
                outline=canvas.hex_to_rgb('#FFF8F0')
            )

            self.animation_frame += 1

        except Exception as e:
            raise WidgetRenderError(f"Erreur lors du rendu de Waveform: {e}") from e


class VUMeter(Widget):
    """
    VU-mètre vertical (indicateur de niveau audio)

    Affiche un niveau vertical avec peak hold
    """

    def __init__(
        self,
        col: int,
        row: int,
        height: int = 1,
        level: float = 0.0,
        bg_color: str = '#1A1110',
        low_color: str = '#4CAF50',
        mid_color: str = '#FFB627',
        high_color: str = '#FF6B35',
        peak_color: str = '#FF0000'
    ):
        """
        Initialise le VU-mètre

        Args:
            col: Colonne
            row: Rangée de départ
            height: Hauteur en boutons
            level: Niveau (0.0 à 1.0)
            bg_color: Couleur de fond
            low_color: Couleur niveau bas (vert)
            mid_color: Couleur niveau moyen (jaune)
            high_color: Couleur niveau élevé (orange)
            peak_color: Couleur peak (rouge)

        Raises:
            WidgetSizeError: Si hauteur invalide
            ColorError: Si couleur invalide
        """
        super().__init__(col, row, 1, height)

        validate_widget_size(1, height)
        validate_color(bg_color)
        validate_color(low_color)
        validate_color(mid_color)
        validate_color(high_color)
        validate_color(peak_color)

        self.level = safe_clamp(level, 0.0, 1.0)
        self.bg_color = bg_color
        self.low_color = low_color
        self.mid_color = mid_color
        self.high_color = high_color
        self.peak_color = peak_color
        self.peak_hold = 0.0
        self.peak_hold_time = 0

    def set_level(self, value: float) -> None:
        """Met à jour le niveau (0.0 à 1.0)"""
        validate_type(value, (int, float), 'value')
        value = safe_clamp(float(value), 0.0, 1.0)

        self.level = value

        # Peak hold
        if self.level > self.peak_hold:
            self.peak_hold = self.level
            self.peak_hold_time = 30  # Frames
        elif self.peak_hold_time > 0:
            self.peak_hold_time -= 1
        else:
            self.peak_hold = max(0.0, self.peak_hold - 0.01)

    def render(self, canvas: StreamDeckCanvas) -> None:
        """Rend le VU-mètre"""
        if not self.visible:
            return

        try:
            self.validate_bounds(canvas)

            x, y, w, h = canvas.get_region_rect(self.col, self.row, 1, self.height)

            # Fond (utilise draw_rounded_rect)
            canvas.draw_rounded_rect(
                self.col, self.row,
                width_cols=1,
                height_rows=self.height,
                color=self.bg_color,
                border='#4A4543',
                border_width=1,
                radius=8
            )

            # Barres de niveau
            num_bars = 20 * self.height
            bar_height = (h - 12) / num_bars  # Padding de 6 par côté
            active_bars = int(num_bars * self.level)

            for i in range(active_bars):
                bar_y = y + h - 6 - (i + 1) * bar_height

                # Couleur selon le niveau
                if i < num_bars * 0.6:
                    color = self.low_color
                elif i < num_bars * 0.85:
                    color = self.mid_color
                elif i < num_bars * 0.95:
                    color = self.high_color
                else:
                    color = self.peak_color

                # Dessiner la barre
                canvas.draw.rectangle(
                    [x + 10, int(bar_y),
                     x + w - 10, int(bar_y + bar_height - 1)],
                    fill=canvas.hex_to_rgb(color)
                )

            # Peak hold indicator
            if self.peak_hold > 0:
                peak_y = y + h - 6 - (num_bars * self.peak_hold) * bar_height
                canvas.draw.line(
                    [(x + 8, int(peak_y)),
                     (x + w - 8, int(peak_y))],
                    fill=canvas.hex_to_rgb('#FFF8F0'),
                    width=2
                )

        except Exception as e:
            raise WidgetRenderError(f"Erreur lors du rendu de VUMeter: {e}") from e


class Timer(Widget):
    """
    Affichage de temps (MM:SS / MM:SS)

    Affiche un temps courant et un temps total
    """

    def __init__(
        self,
        col: int,
        row: int,
        current_time: float = 0.0,
        total_time: float = 300.0,
        color: str = '#FFF8F0',
        bg_color: Optional[str] = None
    ):
        """
        Initialise le timer

        Args:
            col: Colonne
            row: Rangée
            current_time: Temps courant en secondes
            total_time: Temps total en secondes
            color: Couleur du texte
            bg_color: Couleur de fond (None = transparent)

        Raises:
            ColorError: Si couleur invalide
            InvalidParameterError: Si temps invalide
        """
        super().__init__(col, row, 1, 1)

        validate_type(current_time, (int, float), 'current_time')
        validate_type(total_time, (int, float), 'total_time')
        validate_color(color)

        if total_time <= 0:
            raise InvalidParameterError("total_time doit être > 0")

        if bg_color is not None:
            validate_color(bg_color)

        self.current_time = max(0.0, float(current_time))
        self.total_time = max(0.0, float(total_time))
        self.color = color
        self.bg_color = bg_color

    def set_time(self, current: float, total: Optional[float] = None) -> None:
        """
        Met à jour le temps

        Args:
            current: Nouveau temps courant
            total: Nouveau temps total (optionnel)

        Raises:
            InvalidParameterError: Si temps invalide
        """
        validate_type(current, (int, float), 'current')
        if current < 0:
            raise InvalidParameterError("current_time doit être >= 0")

        self.current_time = float(current)

        if total is not None:
            validate_type(total, (int, float), 'total')
            if total <= 0:
                raise InvalidParameterError("total_time doit être > 0")
            self.total_time = float(total)

    def _format_time(self, seconds: float) -> str:
        """Formate un temps en secondes en MM:SS"""
        seconds = max(0, int(seconds))
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def render(self, canvas: StreamDeckCanvas) -> None:
        """Rend le timer"""
        if not self.visible:
            return

        try:
            self.validate_bounds(canvas)

            # Fond optionnel
            if self.bg_color:
                canvas.draw_rect(
                    self.col, self.row,
                    color=self.bg_color,
                    radius=10
                )

            # Formatage du temps
            time_text = f"{self._format_time(self.current_time)}\n{self._format_time(self.total_time)}"

            canvas.draw_text(
                self.col, self.row,
                text=time_text,
                color=self.color,
                size='normal',
                align='center'
            )

        except Exception as e:
            raise WidgetRenderError(f"Erreur lors du rendu de Timer: {e}") from e


class ScrollingText(Widget):
    """
    Texte défilant horizontal (pour noms de fichiers longs)

    Affiche un texte plus long que la zone en le faisant défiler
    """

    def __init__(
        self,
        col: int,
        row: int,
        width: int,
        text: str = "",
        color: str = '#FFF8F0',
        bg_color: str = '#1A1110',
        speed: int = 2
    ):
        """
        Initialise le texte défilant

        Args:
            col: Colonne de départ
            row: Rangée de départ
            width: Largeur en boutons
            text: Texte à afficher
            color: Couleur du texte
            bg_color: Couleur de fond
            speed: Vitesse de défilement

        Raises:
            WidgetSizeError: Si largeur invalide
            ColorError: Si couleur invalide
            InvalidParameterError: Si vitesse invalide
        """
        super().__init__(col, row, width, 1)

        validate_widget_size(width, 1)
        validate_type(text, str, 'text')
        validate_color(color)
        validate_color(bg_color)
        validate_positive_nonzero(speed, 'speed')

        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.speed = speed
        self.offset = 0
        self.frame_count = 0

    def set_text(self, text: str) -> None:
        """Change le texte"""
        validate_type(text, str, 'text')
        self.text = text
        self.offset = 0

    def render(self, canvas: StreamDeckCanvas) -> None:
        """Rend le texte défilant"""
        if not self.visible:
            return

        try:
            self.validate_bounds(canvas)

            x, y, w, h = canvas.get_region_rect(self.col, self.row, self.width, self.height)

            # Fond
            canvas.draw.rectangle(
                [x, y, x + w, y + h],
                fill=canvas.hex_to_rgb(self.bg_color)
            )

            # Mesurer le texte
            font = canvas.fonts['normal']
            bbox = canvas.draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]

            # Si le texte est plus large que la zone, on le fait défiler
            if text_width > w - 20:
                self.frame_count += 1
                if self.frame_count % 3 == 0:  # Ralentir l'animation
                    self.offset += self.speed
                    if self.offset > text_width:
                        self.offset = -w
            else:
                self.offset = 0

            # Dessiner le texte avec offset
            text_x = x + 10 - self.offset
            text_y = y + h // 2

            # Utiliser text_at_pos pour la position en pixels
            canvas.text_at_pos(
                text_x, text_y,
                text=self.text,
                color=self.color,
                size='normal',
                anchor='lm'
            )

        except Exception as e:
            raise WidgetRenderError(f"Erreur lors du rendu de ScrollingText: {e}") from e


class LoadingSpinner(Widget):
    """
    Spinner de chargement animé

    Affiche des points en rotation pour indiquer un chargement
    """

    def __init__(
        self,
        col: int,
        row: int,
        color: str = '#F7931E',
        bg_color: Optional[str] = None
    ):
        """
        Initialise le spinner

        Args:
            col: Colonne
            row: Rangée
            color: Couleur du spinner
            bg_color: Couleur de fond (optionnel)

        Raises:
            ColorError: Si couleur invalide
        """
        super().__init__(col, row, 1, 1)

        validate_color(color)
        if bg_color is not None:
            validate_color(bg_color)

        self.color = color
        self.bg_color = bg_color
        self.angle = 0

    def render(self, canvas: StreamDeckCanvas) -> None:
        """Rend le spinner"""
        if not self.visible:
            return

        try:
            self.validate_bounds(canvas)

            x, y, w, h = canvas.get_button_rect(self.col, self.row)

            # Fond optionnel
            if self.bg_color:
                canvas.draw_rect(
                    self.col, self.row,
                    color=self.bg_color,
                    radius=10
                )

            center_x = x + w // 2
            center_y = y + h // 2
            radius = 20

            # Dessiner des points en cercle
            num_points = 8
            for i in range(num_points):
                angle = (self.angle + i * (360 / num_points)) * (math.pi / 180)
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))

                # Taille variable pour effet de traînée
                size = 2 + int(3 * (1 - i / num_points))

                canvas.draw.ellipse(
                    [px - size, py - size, px + size, py + size],
                    fill=canvas.hex_to_rgb(self.color)
                )

            self.angle = (self.angle + 15) % 360

        except Exception as e:
            raise WidgetRenderError(f"Erreur lors du rendu de LoadingSpinner: {e}") from e


class Grid(Widget):
    """
    Grille visuelle pour le layout (debug)

    Affiche une grille avec numéros pour déboguer les positions
    """

    def __init__(
        self,
        cols: int,
        rows: int,
        color: str = '#4A4543',
        show_numbers: bool = True
    ):
        """
        Initialise la grille

        Args:
            cols: Nombre de colonnes
            rows: Nombre de rangées
            color: Couleur de la grille
            show_numbers: Afficher les numéros

        Raises:
            WidgetSizeError: Si dimensions invalides
            ColorError: Si couleur invalide
        """
        super().__init__(0, 0, cols, rows)

        validate_positive_nonzero(cols, 'cols')
        validate_positive_nonzero(rows, 'rows')
        validate_color(color)
        validate_type(show_numbers, bool, 'show_numbers')

        self.grid_cols = cols
        self.grid_rows = rows
        self.color = color
        self.show_numbers = show_numbers

    def render(self, canvas: StreamDeckCanvas) -> None:
        """Rend la grille"""
        if not self.visible:
            return

        try:
            # Lignes verticales
            for col in range(self.grid_cols + 1):
                x = col * canvas.button_size
                canvas.draw_line(
                    x, 0, x, canvas.height,
                    color=self.color,
                    width=1
                )

            # Lignes horizontales
            for row in range(self.grid_rows + 1):
                y = row * canvas.button_size
                canvas.draw_line(
                    0, y, canvas.width, y,
                    color=self.color,
                    width=1
                )

            # Numéros
            if self.show_numbers:
                index = 0
                for row in range(self.grid_rows):
                    for col in range(self.grid_cols):
                        canvas.draw_text(
                            col, row,
                            text=str(index),
                            color=self.color,
                            size='small',
                            align='top',
                            offset_y=5
                        )
                        index += 1

        except Exception as e:
            raise WidgetRenderError(f"Erreur lors du rendu de Grid: {e}") from e


# ============= GESTIONNAIRE DE WIDGETS =============

class WidgetManager:
    """
    Gestionnaire de widgets pour faciliter la création de layouts

    Gère une collection de widgets avec rendu et hit testing
    """

    def __init__(self):
        """Initialise le gestionnaire"""
        self.widgets: List[Widget] = []

    def add(self, widget: Widget) -> Widget:
        """
        Ajoute un widget

        Args:
            widget: Widget à ajouter

        Returns:
            Le widget ajouté (pour chaining)

        Raises:
            InvalidWidgetTypeError: Si widget invalide
        """
        validate_type(widget, Widget, 'widget')

        self.widgets.append(widget)
        return widget

    def remove(self, widget: Widget) -> None:
        """
        Retire un widget

        Args:
            widget: Widget à retirer
        """
        if widget in self.widgets:
            self.widgets.remove(widget)

    def clear(self) -> None:
        """Efface tous les widgets"""
        self.widgets.clear()

    def render_all(self, canvas: StreamDeckCanvas) -> None:
        """
        Rend tous les widgets visibles

        Args:
            canvas: Canvas de rendu

        Raises:
            WidgetRenderError: Si erreur de rendu
        """
        validate_type(canvas, StreamDeckCanvas, 'canvas')

        for widget in self.widgets:
            if widget.visible:
                try:
                    widget.render(canvas)
                except WidgetRenderError:
                    # Log l'erreur mais continue avec les autres widgets
                    print(f"⚠️  Erreur de rendu widget {widget.__class__.__name__}")
                    continue

    def find_widget_at(self, col: int, row: int) -> Optional[Widget]:
        """
        Trouve le widget à une position donnée

        Args:
            col: Colonne
            row: Rangée

        Returns:
            Widget trouvé ou None

        Raises:
            InvalidParameterError: Si coordonnées invalides
        """
        validate_type(col, int, 'col')
        validate_type(row, int, 'row')

        for widget in reversed(self.widgets):  # Du dessus vers le dessous
            if widget.visible and widget.is_point_inside(col, row):
                return widget
        return None

    def get_widgets_by_type(self, widget_type) -> List[Widget]:
        """
        Retourne tous les widgets d'un type donné

        Args:
            widget_type: Type de widget à chercher

        Returns:
            Liste des widgets du type spécifié
        """
        return [w for w in self.widgets if isinstance(w, widget_type)]

    def get_widget_count(self) -> int:
        """Retourne le nombre de widgets"""
        return len(self.widgets)

    def __len__(self) -> int:
        """Support de len()"""
        return len(self.widgets)

    def __iter__(self):
        """Support de l'itération"""
        return iter(self.widgets)

    def __repr__(self) -> str:
        return f"WidgetManager({len(self.widgets)} widgets)"
