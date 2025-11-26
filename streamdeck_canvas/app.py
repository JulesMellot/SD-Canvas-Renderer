"""
Application Wrapper pour Stream Deck Canvas

Simplifie la création d'applications en gérant:
- Détection automatique du device
- Initialisation du renderer
- Boucle principale
- Gestion des erreurs
- Nettoyage
"""

from typing import Optional, Callable, List
import time
from abc import ABC, abstractmethod
import signal
import sys

try:
    from StreamDeck.DeviceManager import DeviceManager
    STREAMDECK_AVAILABLE = True
except ImportError:
    try:
        from streamdeck import DeviceManager
        STREAMDECK_AVAILABLE = True
    except ImportError:
        STREAMDECK_AVAILABLE = False

from .renderer import StreamDeckRenderer, DebugRenderer
from .canvas import StreamDeckCanvas
from .widgets import WidgetManager


class StreamDeckApp:
    """
    Classe principale pour créer une application Stream Deck rapidement.
    
    Exemple:
        app = StreamDeckApp()
        
        @app.on_setup
        def setup(canvas, widgets):
            widgets.add(Button(...))
            
        @app.on_loop
        def loop(canvas, widgets, delta_time):
            # Animation logic
            pass
            
        app.run()
    """

    def __init__(
        self,
        target_fps: int = 15,
        use_hardware: bool = True,
        debug_cols: int = 5,
        debug_rows: int = 3
    ):
        """
        Initialise l'application

        Args:
            target_fps: FPS cible
            use_hardware: Si True, tente d'utiliser un vrai Stream Deck
            debug_cols: Colonnes pour le mode debug (si pas de hardware)
            debug_rows: Rangées pour le mode debug
        """
        self.target_fps = target_fps
        self.use_hardware = use_hardware
        self.debug_cols = debug_cols
        self.debug_rows = debug_rows
        
        self.renderer = None
        self.widgets = WidgetManager()
        
        # Callbacks
        self._setup_callback = None
        self._loop_callback = None
        self._cleanup_callback = None
        
        # Gestion des signaux (Ctrl+C)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def on_setup(self, func: Callable):
        """Décorateur pour la fonction de setup"""
        self._setup_callback = func
        return func

    def on_loop(self, func: Callable):
        """Décorateur pour la fonction de boucle"""
        self._loop_callback = func
        return func

    def on_cleanup(self, func: Callable):
        """Décorateur pour la fonction de nettoyage"""
        self._cleanup_callback = func
        return func

    def _init_renderer(self):
        """Initialise le renderer approprié"""
        deck = None
        
        if self.use_hardware and STREAMDECK_AVAILABLE:
            try:
                manager = DeviceManager()
                decks = manager.enumerate()
                if decks:
                    deck = decks[0]
                    deck.open()
                    deck.reset()
                    print(f"✅ Stream Deck trouvé: {deck.deck_type()}")
                    self.renderer = StreamDeckRenderer(deck, target_fps=self.target_fps)
                else:
                    print("⚠️  Aucun Stream Deck trouvé. Passage en mode Debug.")
            except Exception as e:
                print(f"⚠️  Erreur lors de l'initialisation hardware: {e}")
        
        if self.renderer is None:
            print(f"🐛 Mode Debug activé ({self.debug_cols}x{self.debug_rows})")
            self.renderer = DebugRenderer(
                cols=self.debug_cols,
                rows=self.debug_rows,
                target_fps=self.target_fps
            )

    def _render_callback(self, canvas: StreamDeckCanvas, frame_count: int, delta_time: float):
        """Callback interne de rendu"""
        # Logique utilisateur
        if self._loop_callback:
            self._loop_callback(canvas, self.widgets, delta_time)
            
        # Rendu des widgets
        self.widgets.render_all(canvas)

    def run(self):
        """Lance l'application"""
        try:
            self._init_renderer()
            
            # Setup utilisateur
            if self._setup_callback:
                print("⚙️  Configuration de l'application...")
                self._setup_callback(self.renderer.canvas, self.widgets)
            
            # Lancement du renderer
            print("🚀 Application démarrée (Ctrl+C pour quitter)")
            
            # Utilisation du context manager nouvellement ajouté
            with self.renderer:
                self.renderer.start(render_callback=self._render_callback)
                
        except KeyboardInterrupt:
            pass  # Géré par le signal handler ou context manager
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()

    def _cleanup(self):
        """Nettoyage final"""
        print("\n🧹 Nettoyage...")
        if self._cleanup_callback:
            try:
                self._cleanup_callback()
            except Exception as e:
                print(f"Erreur lors du cleanup utilisateur: {e}")
                
        # Si c'était un vrai device, on ferme la connexion
        if isinstance(self.renderer, StreamDeckRenderer) and self.renderer.deck:
             try:
                 self.renderer.deck.close()
             except:
                 pass

    def _signal_handler(self, sig, frame):
        """Gestionnaire de signaux"""
        print("\n🛑 Signal d'arrêt reçu")
        if self.renderer:
            self.renderer.stop()
        sys.exit(0)
