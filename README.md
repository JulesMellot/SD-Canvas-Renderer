# Stream Deck Canvas Renderer

🎨 Un moteur de rendu temps réel pour Elgato Stream Deck basé sur un canvas unifié.

## Pourquoi ?

Au lieu de générer 15 images individuelles pour chaque bouton du Stream Deck, ce moteur :
- Crée un **canvas unique** (360×216px pour Stream Deck classique)
- Permet de dessiner comme sur une surface normale
- Découpe automatiquement en tiles pour chaque bouton
- Supporte les **animations fluides** et les **éléments multi-boutons**

## Installation
```bash
pip install streamdeck-canvas-renderer
```

Ou depuis les sources :
```bash
git clone https://github.com/yourusername/streamdeck-canvas-renderer.git
cd streamdeck-canvas-renderer
pip install -e .
```

## Quick Start
```python
from streamdeck_canvas import StreamDeckCanvas, StreamDeckRenderer
from streamdeck import DeviceManager

# Initialiser le Stream Deck
deck_manager = DeviceManager()
deck = deck_manager.enumerate()[0]
deck.open()
deck.reset()

# Créer le renderer
renderer = StreamDeckRenderer(deck)
canvas = renderer.canvas

# Dessiner
canvas.draw_text(2, 1, "Hello!", color='#FF6B35', size='large')
canvas.draw_rect(0, 0, 1, 1, color='#F7931E')

# Mettre à jour le Stream Deck
renderer.update()

# Nettoyer
deck.close()
```

## Concepts

### Canvas Unifié
Le Stream Deck est traité comme un **canvas de 5×3 boutons** (ou selon votre modèle).
Vous dessinez sur ce canvas et le renderer s'occupe de tout.

### Coordonnées
- **En boutons** : `(col, row)` de 0 à 4 (cols) et 0 à 2 (rows)
- **En pixels** : Chaque bouton = 72×72px

### Widgets multi-boutons
Créez des éléments qui s'étendent sur plusieurs boutons :
```python
# Barre de progression sur 3 boutons
canvas.draw_progress_bar(start_col=1, row=1, width=3, progress=0.65)
```

## Documentation complète

Voir [docs/](docs/) pour plus d'exemples et d'API.

## Compatibilité

- Stream Deck (classique) : 5×3 boutons, 72×72px
- Stream Deck Mini : 3×2 boutons, 80×80px
- Stream Deck XL : 8×4 boutons, 96×96px

Le renderer détecte automatiquement votre modèle.

## License

MIT
```

---

## **requirements.txt**
```
Pillow>=10.0.0
streamdeck>=0.9.0
numpy>=1.24.0