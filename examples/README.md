# Exemples Stream Deck Canvas Renderer

Ce dossier contient des exemples qui démontrent les capacités du Stream Deck Canvas Renderer.

## 🚀 Démarrage rapide

### Installation
```bash
# Depuis la racine du projet
pip install -e .
```

### Lancer les exemples
```bash
# 📱 Détecter les appareils Stream Deck connectés
python examples/detect_devices.py

# 🎯 Exemples en mode debug (sans appareil physique)
python examples/basic_usage.py                    # Simple et rapide
python examples/showcase.py                      # Démonstration complète
python examples/audio_monitor.py                 # Interface audio
python examples/dashboard.py                     # Dashboard système

# 🎮 Exemple avec appareil réel (nécessite un Stream Deck)
python examples/real_device.py

# 🛠️ Exemples avec les nouvelles fonctions utilitaires
python examples/quick_start.py          # Connection automatique ultra-simple
python examples/advanced_manager.py     # Gestion avancée des appareils
```

## 📁 Description des exemples

### `detect_devices.py` 📱
**Utilitaire de détection**
Détecte et affiche les informations des Stream Deck connectés :
- Liste des appareils disponibles
- Informations détaillées (modèle, firmware, layout)
- Compatibilité avec le renderer
- Dépannage des erreurs de connexion

### `basic_usage.py`
**Niveau : Débutant**
Exemple minimal pour comprendre les bases :
- Création d'un renderer debug
- Ajout de widgets simples
- Rendu de base

### `showcase.py` ⭐
**Niveau : Complet**
Démonstration complète de toutes les fonctionnalités :
- Navigation et contrôles interactifs
- Visualisation audio (waveform, VU-mètres)
- Animations fluides basées sur le temps
- Widgets multi-boutons
- Texte défilant
- Indicateurs de progression

### `audio_monitor.py`
**Niveau : Intermédiaire**
Simulation d'un moniteur audio professionnel :
- Contrôles de transport (play/pause/stop/record)
- Waveform avec markers et position
- VU-mètres stéréo avec peak hold
- Timer et durée
- Détection de peaks audio

### `dashboard.py`
**Niveau : Intermédiaire**
Dashboard système en temps réel :
- Monitoring CPU/Memory/Réseau
- Indicateurs visuels avec seuils de couleur
- Compteurs de processus
- Alertes système
- Uptime et statuts

### `real_device.py` 🎮
**Niveau : Avancé**
Interface complète avec un vrai Stream Deck :
- Détection automatique de l'appareil
- Gestion des événements de boutons
- Contrôles multimédia interactifs
- Animation en temps réel sur appareil
- Gestion de la luminosité
- Interface utilisateur fonctionnelle

### `quick_start.py` 🚀
**Niveau : Débutant**
Utilisation des nouvelles fonctions utilitaires :
- Détection automatique avec fallback debug
- Connection en 1 ligne de code
- Interface simple et fonctionnelle
- Gestion transparente des erreurs

### `advanced_manager.py` 🛠️
**Niveau : Avancé**
Gestion avancée avec StreamDeckManager :
- Détection complète des appareils
- Informations détaillées (modèle, firmware, layout)
- Interface adaptative selon la taille de l'appareil
- Gestion propre des connexions
- Support multi-appareils

## 🎨 Concepts illustrés

### Architecture
- **Canvas unifié** : Dessin sur un seul grand canvas
- **Système de widgets** : Composants réutilisables
- **Gestionnaire de widgets** : Organisation et rendu automatique
- **Mode debug** : Développement sans matériel

### Widgets utilisés
- `Button` : Boutons interactifs avec icônes
- `Waveform` : Visualisation audio avec animation
- `VUMeter` : Indicateurs de niveau audio
- `ProgressBar` : Barres de progression multi-boutons
- `Timer` : Affichage temporel
- `ScrollingText` : Texte défilant pour noms longs
- `LoadingSpinner` : Animations de chargement

### Fonctionnalités avancées
- **Animations fluides** : Utilisation du temps pour les transitions
- **États dynamiques** : Changement de couleurs et apparences
- **Coordonnées multi-boutons** : Widgets qui s'étendent
- **Cycle de rendu** : Frame timing et FPS control
- **Gestion des événements** : États pressed/normal

## 🛠️ Personnalisation

### Changer les couleurs
```python
from streamdeck_canvas.utils import ColorPalette

# Utiliser les couleurs prédéfinies
home_btn.bg_color = ColorPalette.PRIMARY

# Ou utiliser vos propres couleurs
home_btn.bg_color = '#FF6B35'  # Orange
```

### Adapter aux différents Stream Decks
```python
# Stream Deck Classic (5×3, 72px)
renderer = DebugRenderer(cols=5, rows=3, button_size=72)

# Stream Deck Mini (3×2, 80px)
renderer = DebugRenderer(cols=3, rows=2, button_size=80)

# Stream Deck XL (8×4, 96px)
renderer = DebugRenderer(cols=8, rows=4, button_size=96)
```

### Utiliser avec un vrai Stream Deck
```python
from streamdeck_canvas.renderer import StreamDeckRenderer
from streamdeck import DeviceManager

# Remplacer DebugRenderer par StreamDeckRenderer
deck_manager = DeviceManager()
deck = deck_manager.enumerate()[0]
deck.open()
renderer = StreamDeckRenderer(deck)
```

## 🎯 Prochaines étapes

1. **Comprendre l'architecture** : Regardez `streamdeck_canvas/renderer.py` et `canvas.py`
2. **Créer vos propres widgets** : Héritez de la classe `Widget`
3. **Ajouter des interactions** : Utilisez `on_button_press` callback
4. **Optimiser les performances** : FPS control et rendering efficace

## 💡 Idées de projets

- Interface de streaming (OBS, Twitch)
- Contrôleur de musique (Spotify, iTunes)
- Dashboard de monitoring
- Contrôles de jeu
- Interface de développement (git, docker)
- Automatisation domotique

## 🔧 Debug et développement

Les exemples utilisent `DebugRenderer` qui :
- Sauvegarde les frames en PNG
- N'a pas besoin de matériel
- Affiche les FPS dans la console
- Permet le développement itératif

Pour passer en production, remplacez simplement :
```python
# Développement
renderer = DebugRenderer(cols=5, rows=3, button_size=72)

# Production
renderer = StreamDeckRenderer(deck)
```