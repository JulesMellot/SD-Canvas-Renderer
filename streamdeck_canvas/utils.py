"""
Utilitaires pour Stream Deck Canvas
"""

import math
import time
from typing import Tuple, List, Optional, Union
from PIL import Image, ImageDraw, ImageFont


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convertit une couleur hexadécimale en tuple RGB

    Args:
        hex_color: Couleur au format '#RRGGBB' ou 'RRGGBB'

    Returns:
        Tuple (r, g, b) avec des valeurs 0-255

    Examples:
        >>> hex_to_rgb('#FF6B35')
        (255, 107, 53)
        >>> hex_to_rgb('FF6B35')
        (255, 107, 53)
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Couleur hexadécimale invalide: {hex_color}")

    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError as e:
        raise ValueError(f"Couleur hexadécimale invalide: {hex_color}") from e


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convertit un tuple RGB en couleur hexadécimale

    Args:
        r, g, b: Valeurs 0-255

    Returns:
        Couleur au format '#RRGGBB'
    """
    for value in (r, g, b):
        if not 0 <= value <= 255:
            raise ValueError(f"Valeur RGB invalide: {value}. Doit être entre 0 et 255.")

    return f'#{r:02X}{g:02X}{b:02X}'


def interpolate_color(color1: str, color2: str, factor: float) -> str:
    """
    Interpole linéairement entre deux couleurs

    Args:
        color1: Couleur de départ (hex)
        color2: Couleur de fin (hex)
        factor: Facteur d'interpolation (0.0 à 1.0)

    Returns:
        Couleur interpolée (hex)
    """
    factor = max(0.0, min(1.0, factor))

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * factor)
    g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * factor)
    b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * factor)

    return rgb_to_hex(r, g, b)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limite une valeur entre min et max

    Args:
        value: Valeur à limiter
        min_val: Valeur minimale
        max_val: Valeur maximale

    Returns:
        Valeur limitée
    """
    return max(min_val, min(max_val, value))


def lerp(start: float, end: float, factor: float) -> float:
    """
    Interpolation linéaire entre deux valeurs

    Args:
        start: Valeur de départ
        end: Valeur de fin
        factor: Facteur (0.0 à 1.0)

    Returns:
        Valeur interpolée
    """
    return start + (end - start) * clamp(factor, 0.0, 1.0)


def ease_in_out_cubic(t: float) -> float:
    """
    Fonction d'easing cubique ease-in-out

    Args:
        t: Temps normalisé (0.0 à 1.0)

    Returns:
        Temps avec easing appliqué
    """
    t = clamp(t, 0.0, 1.0)
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_elastic(t: float) -> float:
    """
    Fonction d'easing élastique ease-out

    Args:
        t: Temps normalisé (0.0 à 1.0)

    Returns:
        Temps avec easing appliqué
    """
    t = clamp(t, 0.0, 1.0)
    c4 = 2 * math.pi / 3

    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def format_time(seconds: float, show_hours: bool = False) -> str:
    """
    Formate un temps en secondes en chaîne lisible

    Args:
        seconds: Temps en secondes
        show_hours: Afficher les heures si > 1h

    Returns:
        Temps formaté (MM:SS ou HH:MM:SS)
    """
    if show_hours or seconds >= 3600:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


def format_bytes(bytes_count: int) -> str:
    """
    Formate une taille en octets de manière lisible

    Args:
        bytes_count: Taille en octets

    Returns:
        Taille formatée (B, KB, MB, GB)
    """
    if bytes_count == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(bytes_count)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def calculate_fps(frame_times: List[float], window_size: int = 30) -> float:
    """
    Calcule le FPS moyen sur une fenêtre de temps

    Args:
        frame_times: Liste des temps de frame en secondes
        window_size: Taille de la fenêtre (nombre de frames)

    Returns:
        FPS moyen
    """
    if not frame_times:
        return 0.0

    recent_times = frame_times[-window_size:]
    if not recent_times:
        return 0.0

    avg_frame_time = sum(recent_times) / len(recent_times)
    return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0


class Timer:
    """
    Timer simple pour mesurer des durées
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        """Démarre le timer"""
        self.start_time = time.time()
        self.end_time = None

    def stop(self):
        """Arrête le timer"""
        if self.start_time is not None:
            self.end_time = time.time()

    def elapsed(self) -> float:
        """Retourne le temps écoulé en secondes"""
        if self.start_time is None:
            return 0.0

        end = self.end_time or time.time()
        return end - self.start_time

    def elapsed_ms(self) -> float:
        """Retourne le temps écoulé en millisecondes"""
        return self.elapsed() * 1000.0

    def reset(self):
        """Réinitialise le timer"""
        self.start_time = None
        self.end_time = None


class FPSCounter:
    """
    Compteur de FPS avec lissage
    """

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times: List[float] = []
        self.last_frame_time = None
        self.fps = 0.0

    def update(self) -> float:
        """
        Met à jour le compteur et retourne le FPS actuel

        Returns:
            FPS actuel
        """
        current_time = time.time()

        if self.last_frame_time is not None:
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)

            # Garder seulement la fenêtre la plus récente
            if len(self.frame_times) > self.window_size:
                self.frame_times.pop(0)

            # Calculer FPS
            self.fps = calculate_fps(self.frame_times, self.window_size)

        self.last_frame_time = current_time
        return self.fps

    def get_fps(self) -> float:
        """Retourne le FPS actuel sans mettre à jour"""
        return self.fps

    def reset(self):
        """Réinitialise le compteur"""
        self.frame_times.clear()
        self.last_frame_time = None
        self.fps = 0.0


def create_rounded_mask(size: Tuple[int, int], radius: int) -> Image.Image:
    """
    Crée un masque arrondi pour les images

    Args:
        size: Taille du masque (width, height)
        radius: Rayon des coins

    Returns:
        Image PIL en mode L utilisable comme masque
    """
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)

    width, height = size
    radius = min(radius, width // 2, height // 2)

    # Dessiner rectangle arrondi
    draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)

    return mask


def apply_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
    """
    Applique des coins arrondis à une image

    Args:
        image: Image PIL à modifier
        radius: Rayon des coins

    Returns:
        Image avec coins arrondis
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    mask = create_rounded_mask(image.size, radius)
    image.putalpha(mask)

    return image


def load_icon(icon_path: str, size: Tuple[int, int] = None) -> Image.Image:
    """
    Charge une icône et la redimensionne

    Args:
        icon_path: Chemin vers le fichier d'icône
        size: Taille cible (width, height)

    Returns:
        Image PIL chargée et redimensionnée
    """
    try:
        image = Image.open(icon_path)

        # Convertir en RGBA pour la transparence
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Redimensionner si nécessaire
        if size and image.size != size:
            image = image.resize(size, Image.Resampling.LANCZOS)

        return image

    except Exception as e:
        raise FileNotFoundError(f"Impossible de charger l'icône: {icon_path}") from e


def measure_text_size(text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    """
    Mesure la taille d'un texte avec une police

    Args:
        text: Texte à mesurer
        font: Police à utiliser

    Returns:
        Tuple (width, height) du texte
    """
    # Créer une image temporaire pour mesurer
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    bbox = temp_draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    return width, height


def truncate_text(text: str, font: ImageFont.ImageFont, max_width: int,
                 suffix: str = "...") -> str:
    """
    Tronque un texte pour qu'il tienne dans une largeur maximale

    Args:
        text: Texte à tronquer
        font: Police à utiliser
        max_width: Largeur maximale en pixels
        suffix: Suffixe à ajouter si tronqué

    Returns:
        Texte tronqué si nécessaire
    """
    if measure_text_size(text, font)[0] <= max_width:
        return text

    # Binaire search pour trouver la bonne longueur
    low, high = 0, len(text)
    best_text = text

    while low < high:
        mid = (low + high + 1) // 2
        truncated = text[:mid] + suffix
        width = measure_text_size(truncated, font)[0]

        if width <= max_width:
            best_text = truncated
            low = mid
        else:
            high = mid - 1

    return best_text or suffix


# Palettes de couleurs prédéfinies
class ColorPalette:
    """Palettes de couleurs pour le Stream Deck"""

    # Palette principale
    PRIMARY = '#FF6B35'      # Orange principal
    SECONDARY = '#F7931E'    # Orange secondaire
    ACCENT = '#FFB627'       # Jaune accent

    # Neutres
    BACKGROUND = '#1A1110'   # Fond sombre
    SURFACE = '#4A4543'      # Surface
    TEXT_PRIMARY = '#FFF8F0' # Texte principal
    TEXT_SECONDARY = '#CCC2BF' # Texte secondaire

    # Statuts
    SUCCESS = '#4CAF50'      # Vert succès
    WARNING = '#FF9800'      # Orange warning
    ERROR = '#F44336'        # Rouge erreur
    INFO = '#2196F3'         # Bleu info

    # Audio/Vidéo
    AUDIO_LOW = '#4CAF50'    # Vert (niveau bas)
    AUDIO_MID = '#FFB627'    # Jaune (niveau moyen)
    AUDIO_HIGH = '#FF6B35'   # Orange (niveau élevé)
    AUDIO_PEAK = '#F44336'   # Rouge (peak)

    @classmethod
    def get_gradient(cls, steps: int, start_color: str, end_color: str) -> List[str]:
        """
        Génère un dégradé entre deux couleurs

        Args:
            steps: Nombre d'étapes (minimum: 1)
            start_color: Couleur de départ
            end_color: Couleur de fin

        Returns:
            Liste de couleurs hexadécimales

        Raises:
            ValueError: Si steps < 1
        """
        if steps < 1:
            raise ValueError(f"steps doit être >= 1, reçu: {steps}")

        if steps == 1:
            return [start_color]

        return [interpolate_color(start_color, end_color, i / (steps - 1))
                for i in range(steps)]


# ============= UTILITAIRES STREAM DECK =============

class StreamDeckManager:
    """
    Gestionnaire pour détecter et connecter automatiquement les Stream Decks
    """

    def __init__(self):
        self.streamdecks = []
        self.device_manager = None
        self._init_library()

    def _init_library(self):
        """Initialise la librairie StreamDeck si disponible"""
        try:
            from StreamDeck.DeviceManager import DeviceManager
            self.device_manager = DeviceManager
            self.streamdecks_available = True
        except ImportError:
            self.device_manager = None
            self.streamdecks_available = False
            print("⚠️  StreamDeck library non disponible. Installez avec: pip install StreamDeck")

    def detect_devices(self) -> List[dict]:
        """
        Détecte tous les Stream Decks connectés

        Returns:
            Liste d'informations sur les appareils détectés
        """
        if not self.streamdecks_available:
            return []

        try:
            streamdecks = self.device_manager().enumerate()
            devices_info = []

            for i, deck in enumerate(streamdecks):
                try:
                    deck.open()
                    deck.reset()

                    key_image_format = deck.key_image_format()
                    cols, rows = deck.key_layout()
                    size = key_image_format['size'][0]

                    device_info = {
                        'index': i,
                        'deck': deck,
                        'deck_type': deck.deck_type(),
                        'serial': deck.get_serial_number(),
                        'firmware': deck.get_firmware_version(),
                        'cols': cols,
                        'rows': rows,
                        'button_size': size,
                        'total_keys': deck.key_count(),
                        'canvas_size': (cols * size, rows * size),
                        'is_visual': deck.is_visual(),
                        'is_touch': deck.is_touch(),
                        'image_format': key_image_format
                    }

                    devices_info.append(device_info)
                    deck.close()

                except Exception as e:
                    print(f"⚠️  Erreur avec Stream Deck #{i + 1}: {e}")
                    continue

            self.streamdecks = devices_info
            return devices_info

        except Exception as e:
            print(f"❌ Erreur lors de la détection: {e}")
            return []

    def print_devices_info(self):
        """Affiche les informations détaillées des appareils détectés"""
        devices = self.detect_devices()

        if not devices:
            print("❌ Aucun Stream Deck trouvé!")
            self._print_troubleshooting()
            return

        print(f"✅ {len(devices)} Stream Deck(s) trouvé(s)")
        print("=" * 60)

        for device in devices:
            self._print_device_info(device)
            print()

        print("🎯 Configuration pour StreamDeckCanvasRenderer:")
        print("=" * 60)

        for i, device in enumerate(devices):
            cols, rows, size = device['cols'], device['rows'], device['button_size']
            print(f"Appareil #{i + 1} ({device['deck_type']}):")
            print(f"   Debug:   DebugRenderer(cols={cols}, rows={rows}, button_size={size})")
            print(f"   Réel:    StreamDeckRenderer(deck)  # après connexion")

    def _print_device_info(self, device: dict):
        """Affiche les informations d'un appareil"""
        i = device['index'] + 1
        print(f"📱 Stream Deck #{i}")
        print(f"   Modèle:     {device['deck_type']}")
        print(f"   Série:      {device['serial']}")
        print(f"   Firmware:   {device['firmware']}")
        print(f"   Grille:     {device['cols']}×{device['rows']} ({device['total_keys']} touches)")
        print(f"   Canvas:     {device['canvas_size'][0]}×{device['canvas_size'][1]} pixels")

        if device['is_visual']:
            fmt = device['image_format']
            print(f"   Images:    {fmt['size'][0]}×{fmt['size'][1]} pixels, {fmt['format']}")
            print(f"   Touch:      {'Oui' if device['is_touch'] else 'Non'}")
        else:
            print(f"   Visuel:    Non")

    def _print_troubleshooting(self):
        """Affiche les conseils de dépannage"""
        print("\n💡 Dépannage:")
        print("   • Vérifiez que l'appareil est connecté via USB")
        print("   • Assurez-vous que les câbles sont bien branchés")
        print("   • Sur macOS: donnez les permissions USB dans Préférences Système")
        print("   • Sur Linux: ajoutez votre utilisateur au groupe 'input' ou 'plugdev'")
        print("   • Essayez de débrancher/rebrancher l'appareil")
        print("   • Redémarrez l'appareil si nécessaire")

    def connect_first_device(self, reset_deck: bool = True) -> Optional[dict]:
        """
        Connecte automatiquement au premier Stream Deck disponible

        Args:
            reset_deck: Si True, réinitialise le deck à la connexion

        Returns:
            Informations sur l'appareil connecté ou None si échec
        """
        devices = self.detect_devices()

        if not devices:
            print("❌ Aucun Stream Deck à connecter")
            return None

        device = devices[0]
        deck = device['deck']

        try:
            deck.open()

            if reset_deck:
                deck.reset()
                print(f"🔄 Stream Deck réinitialisé")

            print(f"✅ Connecté à {device['deck_type']} (Série: {device['serial']})")
            return device

        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return None

    def connect_device_by_index(self, index: int, reset_deck: bool = True) -> Optional[dict]:
        """
        Connecte à un Stream Deck spécifique par son index

        Args:
            index: Index de l'appareil (0-based)
            reset_deck: Si True, réinitialise le deck à la connexion

        Returns:
            Informations sur l'appareil connecté ou None si échec
        """
        devices = self.detect_devices()

        if not devices:
            print("❌ Aucun Stream Deck disponible")
            return None

        if index < 0 or index >= len(devices):
            print(f"❌ Index {index} invalide. Appareils disponibles: 0-{len(devices)-1}")
            return None

        device = devices[index]
        deck = device['deck']

        try:
            deck.open()

            if reset_deck:
                deck.reset()
                print(f"🔄 Stream Deck #{index + 1} réinitialisé")

            print(f"✅ Connecté à {device['deck_type']} (Index: {index})")
            return device

        except Exception as e:
            print(f"❌ Erreur de connexion au Stream Deck #{index + 1}: {e}")
            return None

    def connect_device_by_serial(self, serial: str, reset_deck: bool = True) -> Optional[dict]:
        """
        Connecte à un Stream Deck spécifique par son numéro de série

        Args:
            serial: Numéro de série de l'appareil
            reset_deck: Si True, réinitialise le deck à la connexion

        Returns:
            Informations sur l'appareil connecté ou None si échec
        """
        devices = self.detect_devices()

        if not devices:
            print("❌ Aucun Stream Deck disponible")
            return None

        device_found = None
        for device in devices:
            if device['serial'] == serial:
                device_found = device
                break

        if not device_found:
            print(f"❌ Aucun Stream Deck trouvé avec le numéro de série: {serial}")
            return None

        deck = device_found['deck']

        try:
            deck.open()

            if reset_deck:
                deck.reset()
                print(f"🔄 Stream Deck {serial} réinitialisé")

            print(f"✅ Connecté à {device_found['deck_type']} (Série: {serial})")
            return device_found

        except Exception as e:
            print(f"❌ Erreur de connexion au Stream Deck {serial}: {e}")
            return None

    def create_renderer(self, device_info: dict = None, debug_mode: bool = False) -> Optional['StreamDeckRenderer']:
        """
        Crée un renderer approprié pour l'appareil

        Args:
            device_info: Informations sur l'appareil (si None, utilise le premier)
            debug_mode: Si True, crée un DebugRenderer même avec appareil disponible

        Returns:
            Instance du renderer ou None si échec
        """
        if debug_mode or not self.streamdecks_available:
            # Mode debug ou librairie non disponible
            if device_info:
                cols, rows, size = device_info['cols'], device_info['rows'], device_info['button_size']
            else:
                # Dimensions par défaut (Stream Deck Classic)
                cols, rows, size = 5, 3, 72

            from .renderer import DebugRenderer
            renderer = DebugRenderer(cols=cols, rows=rows, button_size=size)
            print(f"🐛 DebugRenderer créé: {cols}×{rows} ({size}px)")
            return renderer

        else:
            # Mode appareil réel
            if not device_info:
                device_info = self.connect_first_device()
                if not device_info:
                    return None

            try:
                from .renderer import StreamDeckRenderer
                renderer = StreamDeckRenderer(device_info['deck'])
                print(f"🎮 StreamDeckRenderer créé pour {device_info['deck_type']}")
                return renderer

            except Exception as e:
                print(f"❌ Erreur de création du renderer: {e}")
                return None

    def close_device(self, device_info: dict):
        """
        Ferme proprement la connexion à un Stream Deck

        Args:
            device_info: Informations sur l'appareil à fermer
        """
        try:
            deck = device_info['deck']
            deck.reset()
            deck.set_brightness(50)  # Luminosité par défaut
            deck.close()
            print(f"✅ Stream Deck {device_info['serial']} fermé proprement")

        except Exception as e:
            print(f"⚠️  Erreur lors de la fermeture: {e}")

    def close_all_devices(self):
        """Ferme toutes les connexions aux Stream Decks"""
        for device in self.streamdecks:
            self.close_device(device)
        self.streamdecks.clear()


# Fonction utilitaire pour une utilisation rapide
def connect_stream_deck(index: int = 0, debug_mode: bool = False) -> Optional['StreamDeckRenderer']:
    """
    Fonction utilitaire pour connecter rapidement un Stream Deck

    Args:
        index: Index de l'appareil à connecter (0 pour le premier)
        debug_mode: Forcer l'utilisation du DebugRenderer

    Returns:
        Renderer prêt à utiliser ou None si échec

    Examples:
        >>> # Auto-connexion au premier appareil
        >>> renderer = connect_stream_deck()

        >>> # Connexion au deuxième appareil
        >>> renderer = connect_stream_deck(index=1)

        >>> # Forcer le mode debug
        >>> renderer = connect_stream_deck(debug_mode=True)
    """
    manager = StreamDeckManager()

    if debug_mode:
        return manager.create_renderer(debug_mode=True)

    device = manager.connect_device_by_index(index)
    if not device:
        return None

    return manager.create_renderer(device)


# Fonction pour scanner et afficher les appareils
def scan_stream_decks():
    """
    Scan et affiche tous les Stream Decks connectés

    Returns:
        Liste des informations sur les appareils détectés
    """
    manager = StreamDeckManager()
    devices = manager.detect_devices()

    if devices:
        manager.print_devices_info()
    else:
        print("❌ Aucun Stream Deck trouvé")
        manager._print_troubleshooting()

    return devices