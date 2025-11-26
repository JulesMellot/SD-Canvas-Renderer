"""
Framework de développement rapide de widgets
Simplifie la création de composants pour les utilisateurs.
"""

from typing import Optional, Callable, Any, Dict
from .widgets import Widget
from .canvas import StreamDeckCanvas
import time

class SimpleWidget(Widget):
    """
    Classe de base simplifiée pour les widgets utilisateur.
    Gère automatiquement:
    - L'initialisation (super().__init__)
    - Le stockage des arguments dans self
    - La gestion du temps (delta_time)
    """
    
    def __init__(self, col: int, row: int, width: int = 1, height: int = 1, **kwargs):
        """
        Initialisation automatique.
        Tous les arguments nommés passés ici sont accessibles via self.args.nom
        ou self.nom s'ils ne sont pas réservés.
        """
        super().__init__(col, row, width, height)
        
        # Stockage des propriétés
        self.props = kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
                
        # Gestion du temps
        self._last_time = time.time()
        self.time = 0.0
        
        # Appel du setup utilisateur
        self.setup()

    def setup(self):
        """
        Surchargez cette méthode pour initialiser vos données.
        Appelé une seule fois à la création.
        """
        pass

    def on_update(self, dt: float):
        """
        Logique de mise à jour (animations, calculs).
        Appelé avant chaque rendu.
        """
        pass

    def on_draw(self, canvas: StreamDeckCanvas):
        """
        Code de dessin.
        Utilisez canvas.draw_... ici.
        """
        pass

    def render(self, canvas: StreamDeckCanvas):
        """Méthode interne, ne pas toucher."""
        if not self.visible: return
        
        # Gestion du temps
        now = time.time()
        dt = now - self._last_time
        self._last_time = now
        self.time += dt
        
        # Update logique
        self.on_update(dt)
        
        # Validation bounds (sécurité)
        self.validate_bounds(canvas)
        
        # Dessin
        self.on_draw(canvas)


class FunctionalWidget(Widget):
    """Wrapper pour transformer une fonction en widget"""
    def __init__(self, col, row, width, height, render_fn, **kwargs):
        super().__init__(col, row, width, height)
        self.render_fn = render_fn
        self.kwargs = kwargs
        self.__dict__.update(kwargs) # Expose kwargs as attributes

    def render(self, canvas: StreamDeckCanvas):
        if self.visible:
            self.render_fn(self, canvas)

def functional_widget(width: int = 1, height: int = 1):
    """
    Décorateur pour créer un widget à partir d'une simple fonction.
    
    Usage:
        @functional_widget(width=2)
        def MyRedBox(self, canvas):
            canvas.draw_rect(self.col, self.row, color='red')
            
        # Utilisation:
        widgets.add(MyRedBox(0, 0, label="Hello"))
    """
    def decorator(func):
        def factory(col, row, w=width, h=height, **kwargs):
            # w et h peuvent être surchargés à l'instanciation
            return FunctionalWidget(col, row, w, h, func, **kwargs)
        return factory
    return decorator
