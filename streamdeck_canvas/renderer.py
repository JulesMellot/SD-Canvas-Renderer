"""
Moteur de rendu principal pour Stream Deck

Version refactorisée avec:
- Interface abstraite propre (RendererBase)
- Gestion d'erreurs hardware robuste
- Validation complète des paramètres
- State management clean
- Lifecycle callbacks
- Performance optimizations (FPS counter, timing)
- Gestion de déconnexion/déconnexion automatique
"""

from typing import Optional, Callable, Dict, Any, Tuple
import time
from abc import ABC, abstractmethod
from PIL import Image
import threading
from functools import wraps

try:
    from StreamDeck.DeviceManager import DeviceManager
    STREAMDECK_AVAILABLE = True
except ImportError:
    try:
        from streamdeck import DeviceManager
        STREAMDECK_AVAILABLE = True
    except ImportError:
        STREAMDECK_AVAILABLE = False

from .canvas import StreamDeckCanvas
from .exceptions import (
    RendererError,
    DeviceNotConnectedError,
    DeviceDisconnectedError,
    RenderingError,
    InvalidOrientationError,
    FrameRateError,
    CanvasError,
    HardwareError,
    DeviceNotFoundError,
    DevicePermissionError,
    ImageConversionError,
)
from .validators import (
    validate_orientation,
    validate_framerate,
    validate_type,
    validate_not_none,
)
from .utils import FPSCounter, Timer


# ============= INTERFACE ABSTRAITE =============

class RendererBase(ABC):
    """
    Interface abstraite pour tous les renderers

    Définit le contrat que doivent respecter StreamDeckRenderer et DebugRenderer
    """

    @property
    @abstractmethod
    def canvas(self) -> StreamDeckCanvas:
        """Retourne le canvas associé au renderer"""
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Vérifie si le renderer est en cours d'exécution"""
        pass

    @property
    @abstractmethod
    def frame_count(self) -> int:
        """Retourne le nombre de frames rendues"""
        pass

    @property
    @abstractmethod
    def fps(self) -> float:
        """Retourne le FPS actuel"""
        pass

    @abstractmethod
    def update(self) -> None:
        """Met à jour le rendu"""
        pass

    @abstractmethod
    def start(self) -> None:
        """Démarre le renderer"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Arrête le renderer proprement"""
        pass

    @abstractmethod
    def render_frame(self, render_callback: Optional[Callable] = None) -> None:
        """Rend une frame unique"""
        pass

    def __enter__(self):
        """Support pour le context manager"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Nettoyage automatique à la sortie du context manager"""
        self.stop()


# ============= CALLBACKS LIFECYCLE =============

class RendererCallbacks:
    """
    Gestionnaire de callbacks pour le lifecycle du renderer
    """

    def __init__(self):
        self.on_start: Optional[Callable[[], None]] = None
        self.on_stop: Optional[Callable[[], None]] = None
        self.on_frame: Optional[Callable[[int, float], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        self.on_device_disconnect: Optional[Callable[[], None]] = None
        self.on_button_press: Optional[Callable[[int, int, int], None]] = None


# ============= UTILITAIRES =============

def handle_renderer_errors(func):
    """
    Décorateur pour gérer automatiquement les erreurs de renderer
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            # Appeler le callback d'erreur s'il existe
            if hasattr(self, '_callbacks') and self._callbacks.on_error:
                try:
                    self._callbacks.on_error(e)
                except Exception:
                    pass  # Ignorer erreur dans callback

            # Re-raise l'erreur originale
            raise

    return wrapper


# ============= RENDERER PRINCIPAL =============

class StreamDeckRenderer(RendererBase):
    """
    Renderer pour Stream Deck physique

    Gère:
    - Détection automatique de l'appareil
    - Boucle de rendu avec frame timing
    - Gestion de déconnexion/reconnexion
    - Callbacks lifecycle
    - Gestion d'erreurs hardware
    """

    # Valeurs par défaut
    DEFAULT_FPS = 15
    DEFAULT_BRIGHTNESS = 80
    DEFAULT_ORIENTATION = 'normal'

    # Tailles standard par modèle
    DEVICE_CONFIGS = {
        6: {'cols': 3, 'rows': 2, 'button_size': 80},   # Mini
        15: {'cols': 5, 'rows': 3, 'button_size': 72},  # Classic
        32: {'cols': 8, 'rows': 4, 'button_size': 96},  # XL
    }

    def __init__(
        self,
        deck,
        target_fps: int = DEFAULT_FPS,
        orientation: str = DEFAULT_ORIENTATION,
        brightness: int = DEFAULT_BRIGHTNESS,
        auto_reconnect: bool = True
    ):
        """
        Initialise le renderer

        Args:
            deck: Instance StreamDeck de la librairie streamdeck
            target_fps: FPS cible (défaut: 15)
            orientation: Orientation ('normal', 'rotated', 'h_mirror', 'v_mirror', 'h_mirror_rotated', 'v_mirror_rotated')
            brightness: Luminosité (0-100, défaut: 80)
            auto_reconnect: Reconnexion automatique en cas de déconnexion

        Raises:
            RendererError: Si erreur d'initialisation
            InvalidOrientationError: Si orientation invalide
            FrameRateError: Si FPS invalide
        """
        # Vérifier disponibilité de la librairie
        if not STREAMDECK_AVAILABLE:
            raise HardwareError(
                "StreamDeck library non disponible. "
                "Installez avec: pip install StreamDeck"
            )

        # Validation des paramètres
        validate_type(deck, object, 'deck')
        validate_framerate(target_fps)
        validate_orientation(orientation)
        validate_type(brightness, int, 'brightness')
        validate_type(auto_reconnect, bool, 'auto_reconnect')

        if not 0 <= brightness <= 100:
            raise RendererError(f"Brightness doit être entre 0 et 100, reçu: {brightness}")

        # Attributs principaux
        self.deck = deck
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.orientation = orientation
        self.brightness = brightness
        self.auto_reconnect = auto_reconnect

        # Callbacks
        self._callbacks = RendererCallbacks()

        # Détection des specs du device
        try:
            self._detect_device_specs()
        except Exception as e:
            raise RendererError(f"Erreur lors de la détection du device: {e}") from e

        # Canvas
        self._canvas = StreamDeckCanvas(
            cols=self.cols,
            rows=self.rows,
            button_size=self.button_size
        )

        # État du renderer
        self._running = False
        self._frame_count = 0
        self._fps_counter = FPSCounter(window_size=30)
        self._last_frame_time = 0.0

        # Thread pour la boucle de rendu
        self._render_thread: Optional[threading.Thread] = None
        self._thread_lock = threading.Lock()

        # Gestion device
        self._device_connected = True
        self._device_error_count = 0
        self._max_errors = 10

        # Setup du deck
        self._setup_deck()

    # ============= PROPRIÉTÉS =============

    @property
    def canvas(self) -> StreamDeckCanvas:
        """Retourne le canvas associé"""
        return self._canvas

    @property
    def is_running(self) -> bool:
        """Vérifie si le renderer est en cours d'exécution"""
        return self._running

    @property
    def frame_count(self) -> int:
        """Retourne le nombre de frames rendues"""
        return self._frame_count

    @property
    def fps(self) -> float:
        """Retourne le FPS actuel"""
        return self._fps_counter.get_fps()

    @property
    def device_info(self) -> Dict[str, Any]:
        """Retourne les informations du device"""
        return {
            'type': self.deck.deck_type(),
            'serial': self._safe_get_serial(),
            'firmware': self._safe_get_firmware(),
            'cols': self.cols,
            'rows': self.rows,
            'button_size': self.button_size,
            'total_keys': self.deck.key_count(),
            'brightness': self.brightness,
            'orientation': self.orientation,
            'is_connected': self._device_connected,
        }

    @property
    def stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du renderer"""
        return {
            'frame_count': self._frame_count,
            'fps': self.fps,
            'target_fps': self.target_fps,
            'device_connected': self._device_connected,
            'error_count': self._device_error_count,
            'render_time_ms': self._last_frame_time * 1000,
        }

    # ============= DETECTION DEVICE =============

    def _detect_device_specs(self) -> None:
        """Détecte automatiquement les specs du Stream Deck"""
        try:
            key_count = self.deck.key_count()
            button_size = self.deck.key_image_format()['size'][0]

            # Utiliser la configuration standard si disponible
            if key_count in self.DEVICE_CONFIGS:
                config = self.DEVICE_CONFIGS[key_count]
                self.cols = config['cols']
                self.rows = config['rows']
                self.button_size = config['button_size']
            else:
                # Fallback: estimation générique
                self.button_size = button_size
                self.cols = key_count // 3
                self.rows = 3

                # Ajustements spécifiques si possible
                if hasattr(self.deck, 'key_layout'):
                    try:
                        layout = self.deck.key_layout()
                        self.cols, self.rows = layout
                    except:
                        pass

        except Exception as e:
            raise RendererError(f"Erreur lors de la détection des specs: {e}") from e

    def _safe_get_serial(self) -> str:
        """Récupère le numéro de série de manière sécurisée"""
        try:
            return self.deck.get_serial_number()
        except:
            return "Inconnu"

    def _safe_get_firmware(self) -> str:
        """Récupère la version firmware de manière sécurisée"""
        try:
            return self.deck.get_firmware_version()
        except:
            return "Inconnue"

    # ============= SETUP DEVICE =============

    def _setup_deck(self) -> None:
        """Configure le Stream Deck"""
        try:
            # Luminosité
            self.deck.set_brightness(self.brightness)

            # Callback des touches
            self.deck.set_key_callback(self._handle_key_event)

            print(f"✅ Stream Deck configuré: {self.cols}×{self.rows}, {self.button_size}px")
            print(f"   Brightness: {self.brightness}, Orientation: {self.orientation}")

        except Exception as e:
            raise RendererError(f"Erreur lors de la configuration: {e}") from e

    # ============= CALLBACKS =============

    def set_callback(self, event: str, callback: Callable) -> None:
        """
        Définit un callback lifecycle

        Args:
            event: Type d'événement ('on_start', 'on_stop', 'on_frame', 'on_error', 'on_device_disconnect', 'on_button_press')
            callback: Fonction à appeler

        Raises:
            InvalidParameterError: Si événement invalide
        """
        valid_events = {
            'on_start', 'on_stop', 'on_frame', 'on_error',
            'on_device_disconnect', 'on_button_press'
        }

        if event not in valid_events:
            raise RendererError(f"Événement invalide: {event}. Valeurs: {valid_events}")

        setattr(self._callbacks, event, callback)

    def _handle_key_event(self, deck, key: int, state: bool) -> None:
        """Gère les événements de touche"""
        if state and self._callbacks.on_button_press:
            try:
                # Convertir l'index en (col, row)
                col = key % self.cols
                row = key // self.cols
                self._callbacks.on_button_press(col, row, key)
            except Exception as e:
                if self._callbacks.on_error:
                    self._callbacks.on_error(e)

    # ============= RENDERING =============

    @handle_renderer_errors
    def update(self) -> None:
        """
        Met à jour le Stream Deck avec le canvas actuel

        Raises:
            DeviceDisconnectedError: Si device déconnecté
            RenderingError: Si erreur de rendu
            ImageConversionError: Si erreur de conversion d'image
        """
        if not self._device_connected:
            raise DeviceDisconnectedError("Device non connecté")

        try:
            tiles = self._canvas.get_tiles()

            for i, tile in enumerate(tiles):
                try:
                    native_image = self._pil_to_native(tile)
                    self.deck.set_key_image(i, native_image)
                except Exception as e:
                    # Erreur sur une tile spécifique
                    self._device_error_count += 1
                    if self._device_error_count >= self._max_errors:
                        self._device_connected = False
                        if self._callbacks.on_device_disconnect:
                            self._callbacks.on_device_disconnect()
                        raise DeviceDisconnectedError("Device déconnecté (trop d'erreurs)")

            self._frame_count += 1

        except DeviceDisconnectedError:
            raise
        except Exception as e:
            self._device_error_count += 1
            raise RenderingError(f"Erreur lors de l'update: {e}") from e

    def _pil_to_native(self, image: Image.Image) -> bytes:
        """
        Convertit une image PIL en format natif Stream Deck avec orientation

        Raises:
            ImageConversionError: Si erreur de conversion
        """
        try:
            import io

            # Copier l'image pour éviter de modifier l'original
            img = image.copy()

            # Normaliser en RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Appliquer l'orientation
            img = self._apply_orientation(img)

            # Convertir en JPEG
            with io.BytesIO() as output:
                img.save(output, format='JPEG', quality=85)
                return output.getvalue()

        except Exception as e:
            raise ImageConversionError(f"Erreur de conversion d'image: {e}") from e

    def _apply_orientation(self, img: Image.Image) -> Image.Image:
        """Applique la transformation d'orientation"""
        if self.orientation == 'normal':
            return img
        elif self.orientation == 'rotated':
            return img.rotate(180, expand=True)
        elif self.orientation == 'h_mirror':
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        elif self.orientation == 'v_mirror':
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        elif self.orientation == 'h_mirror_rotated':
            return img.transpose(Image.FLIP_LEFT_RIGHT).rotate(180, expand=True)
        elif self.orientation == 'v_mirror_rotated':
            return img.transpose(Image.FLIP_TOP_BOTTOM).rotate(180, expand=True)
        else:
            raise InvalidOrientationError(f"Orientation inconnue: {self.orientation}")

    # ============= LIFECYCLE =============

    @handle_renderer_errors
    def render_frame(self, render_callback: Optional[Callable] = None) -> None:
        """
        Rend une frame unique

        Args:
            render_callback: Fonction appelée pour dessiner (canvas, frame_count, delta_time)

        Raises:
            CanvasError: Si erreur canvas
            RenderingError: Si erreur de rendu
        """
        timer = Timer()
        timer.start()

        try:
            # Clear canvas
            self._canvas.clear()

            # Appel du callback utilisateur
            if render_callback:
                render_callback(self._canvas, self._frame_count, self._last_frame_time)

            # Update device
            self.update()

        except (CanvasError, RenderingError):
            raise
        except Exception as e:
            raise RenderingError(f"Erreur lors du rendu: {e}") from e
        finally:
            timer.stop()
            self._last_frame_time = timer.elapsed()

    @handle_renderer_errors
    def start(self, render_callback: Optional[Callable] = None) -> None:
        """
        Démarre la boucle de rendu

        Args:
            render_callback: Fonction appelée à chaque frame

        Raises:
            RendererError: Si déjà en cours d'exécution
        """
        if self._running:
            raise RendererError("Renderer déjà en cours d'exécution")

        self._running = True

        if self._callbacks.on_start:
            self._callbacks.on_start()

        try:
            print(f"🎨 Stream Deck Canvas Renderer démarré")
            print(f"   Device: {self.deck.deck_type()}")
            print(f"   Résolution: {self.cols}×{self.rows} ({self.button_size}px par bouton)")
            print(f"   Target FPS: {self.target_fps}")
            print(f"   Canvas: {self._canvas.width}×{self._canvas.height}px")

            last_frame_time = time.time()

            while self._running:
                frame_start = time.time()

                # Render frame
                self.render_frame(render_callback)

                # FPS counter
                fps = self._fps_counter.update()

                # Callback frame
                if self._callbacks.on_frame:
                    try:
                        self._callbacks.on_frame(self._frame_count, fps)
                    except Exception:
                        pass  # Ignorer erreur dans callback

                # Frame timing
                frame_duration = frame_start - last_frame_time
                sleep_time = max(0, self.frame_time - frame_duration)

                if sleep_time > 0:
                    time.sleep(sleep_time)

                last_frame_time = frame_start

        except KeyboardInterrupt:
            print("\n⏹️  Arrêt demandé")
        finally:
            self.stop()

    def stop(self) -> None:
        """Arrête proprement le renderer"""
        if not self._running:
            return

        self._running = False

        try:
            # Vider le canvas
            self._canvas.clear()
            self.update()
        except:
            pass  # Ignorer erreurs lors de l'arrêt

        if self._callbacks.on_stop:
            self._callbacks.on_stop()

        print("✅ Renderer arrêté proprement")

    # ============= GESTION DEVICE =============

    def reconnect(self) -> bool:
        """
        Tente de reconnecter le device

        Returns:
            True si succès, False sinon
        """
        try:
            if self.deck.is_visual():
                self.deck.reset()
                self._device_connected = True
                self._device_error_count = 0
                print(f"✅ Device reconnecté")
                return True
        except Exception as e:
            print(f"⚠️  Échec de reconnexion: {e}")

        return False

    def set_brightness(self, brightness: int) -> None:
        """
        Ajuste la luminosité

        Args:
            brightness: Valeur 0-100

        Raises:
            RendererError: Si valeur invalide
        """
        validate_type(brightness, int, 'brightness')

        if not 0 <= brightness <= 100:
            raise RendererError(f"Brightness doit être entre 0 et 100, reçu: {brightness}")

        try:
            self.deck.set_brightness(brightness)
            self.brightness = brightness
            print(f"💡 Luminosité: {brightness}%")
        except Exception as e:
            raise RendererError(f"Erreur lors du réglage de la luminosité: {e}") from e

    # ============= UTILITAIRES =============

    def __repr__(self) -> str:
        return f"StreamDeckRenderer({self.cols}×{self.rows}, {self.target_fps}fps)"


# ============= DEBUG RENDERER =============

class DebugRenderer(RendererBase):
    """
    Renderer de debug qui sauvegarde les frames au lieu d'envoyer au device

    Utile pour développer sans avoir le device connecté
    """

    def __init__(
        self,
        cols: int = 5,
        rows: int = 3,
        button_size: int = 72,
        target_fps: int = 15,
        debug_dir: str = "./debug_frames"
    ):
        """
        Initialise le debug renderer

        Args:
            cols: Nombre de colonnes
            rows: Nombre de rangées
            button_size: Taille des boutons
            target_fps: FPS cible
            debug_dir: Répertoire de sauvegarde des frames
        """
        validate_type(cols, int, 'cols')
        validate_type(rows, int, 'rows')
        validate_type(button_size, int, 'button_size')
        validate_framerate(target_fps)
        validate_type(debug_dir, str, 'debug_dir')

        # Attributs
        self.cols = cols
        self.rows = rows
        self.button_size = button_size
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.debug_dir = debug_dir

        # Canvas
        self._canvas = StreamDeckCanvas(
            cols=cols,
            rows=rows,
            button_size=button_size
        )

        # État
        self._running = False
        self._frame_count = 0
        self._fps_counter = FPSCounter(window_size=30)
        self._last_frame_time = 0.0

        # Callbacks
        self._callbacks = RendererCallbacks()

        print(f"🐛 Debug Renderer initialisé: {cols}×{rows} ({button_size}px)")

    # ============= PROPRIÉTÉS =============

    @property
    def canvas(self) -> StreamDeckCanvas:
        return self._canvas

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def fps(self) -> float:
        return self._fps_counter.get_fps()

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            'frame_count': self._frame_count,
            'fps': self.fps,
            'target_fps': self.target_fps,
            'debug_dir': self.debug_dir,
        }

    # ============= CALLBACKS =============

    def set_callback(self, event: str, callback: Callable) -> None:
        """Définit un callback (voir RendererBase.set_callback)"""
        valid_events = {
            'on_start', 'on_stop', 'on_frame', 'on_error',
            'on_device_disconnect', 'on_button_press'
        }

        if event not in valid_events:
            raise RendererError(f"Événement invalide: {event}")

        setattr(self._callbacks, event, callback)

    # ============= RENDERING =============

    @handle_renderer_errors
    def update(self) -> None:
        """Sauvegarde le canvas au lieu d'envoyer au device"""
        import os
        os.makedirs(self.debug_dir, exist_ok=True)

        filename = os.path.join(self.debug_dir, f"debug_frame_{self._frame_count:04d}.png")

        try:
            self._canvas.save_debug(filename)

            if self._frame_count % 30 == 0:
                print(f"💾 Frame {self._frame_count} sauvegardée: {filename}")

        except Exception as e:
            raise RenderingError(f"Erreur de sauvegarde: {e}") from e

    @handle_renderer_errors
    def render_frame(self, render_callback: Optional[Callable] = None) -> None:
        """Rend une frame (mode debug)"""
        timer = Timer()
        timer.start()

        try:
            # Clear canvas
            self._canvas.clear()

            # Callback utilisateur
            if render_callback:
                render_callback(self._canvas, self._frame_count, self._last_frame_time)

            # Sauvegarder
            self.update()

            self._frame_count += 1

        except Exception as e:
            raise RenderingError(f"Erreur de rendu: {e}") from e
        finally:
            timer.stop()
            self._last_frame_time = timer.elapsed()

    # ============= LIFECYCLE =============

    @handle_renderer_errors
    def start(self, render_callback: Optional[Callable] = None) -> None:
        """Démarre la boucle de debug"""
        if self._running:
            raise RendererError("DebugRenderer déjà en cours d'exécution")

        self._running = True

        if self._callbacks.on_start:
            self._callbacks.on_start()

        try:
            print(f"🎨 Debug Renderer démarré")
            print(f"   Résolution: {self.cols}×{self.rows} ({self.button_size}px par bouton)")
            print(f"   Target FPS: {self.target_fps}")
            print(f"   Canvas: {self._canvas.width}×{self._canvas.height}px")
            print(f"   Répertoire debug: {self.debug_dir}")

            last_frame_time = time.time()

            while self._running:
                frame_start = time.time()

                # Render
                self.render_frame(render_callback)

                # FPS
                fps = self._fps_counter.update()

                # Callback
                if self._callbacks.on_frame:
                    try:
                        self._callbacks.on_frame(self._frame_count, fps)
                    except Exception:
                        pass

                # Timing
                frame_duration = frame_start - last_frame_time
                sleep_time = max(0, self.frame_time - frame_duration)

                if sleep_time > 0:
                    time.sleep(sleep_time)

                last_frame_time = frame_start

        except KeyboardInterrupt:
            print("\n⏹️  Arrêt demandé")
        finally:
            self.stop()

    def stop(self) -> None:
        """Arrête le debug renderer"""
        if not self._running:
            return

        self._running = False

        if self._callbacks.on_stop:
            self._callbacks.on_stop()

        print("✅ Debug renderer arrêté")

    # ============= UTILITAIRES =============

    def __repr__(self) -> str:
        return f"DebugRenderer({self.cols}×{self.rows}, {self.target_fps}fps)"
