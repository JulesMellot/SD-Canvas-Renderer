#!/usr/bin/env python3
"""
Stream Deck Canvas Renderer - Quick Start
Exemple ultra-simple avec les nouvelles fonctions utilitaires
"""

from streamdeck_canvas import (
    connect_stream_deck, scan_stream_decks,
    Button, WidgetManager, ColorPalette
)


def main():
    """Exemple ultra-simple de démarrage rapide"""

    print("🚀 Stream Deck Canvas Renderer - Quick Start")
    print("=" * 50)

    # 1. Scanner les appareils disponibles
    print("📱 Scan des appareils...")
    devices = scan_stream_decks()

    if not devices:
        print("⚠️  Pas d'appareil réel, utilisation du mode debug")
        print("   Installez la librairie StreamDeck pour utiliser un vrai appareil:")
        print("   pip install StreamDeck")

    # 2. Connecter automatiquement (debug ou premier appareil)
    print("\n🔌 Connexion automatique...")
    renderer = connect_stream_deck(debug_mode=len(devices) == 0)

    if not renderer:
        print("❌ Erreur de connexion")
        return

    canvas = renderer.canvas
    widgets = WidgetManager()

    print(f"✅ Renderer créé: {renderer.cols}×{renderer.rows} ({renderer.button_size}px)")

    # 3. Créer une interface simple
    widgets.add(Button(0, 0, "🏠", "HOME", bg_color=ColorPalette.PRIMARY))
    widgets.add(Button(1, 0, "⚙️", "SET", bg_color=ColorPalette.SURFACE))
    widgets.add(Button(2, 0, "🎵", "MUSIC", bg_color=ColorPalette.SUCCESS))
    widgets.add(Button(3, 0, "🌐", "WEB", bg_color=ColorPalette.INFO))
    widgets.add(Button(4, 0, "✕", "EXIT", bg_color=ColorPalette.ERROR))

    # Texte de bienvenue
    widgets.add(Button(1, 1, "👋", "HELLO!", bg_color=ColorPalette.BACKGROUND))
    widgets.add(Button(2, 1, "🎨", "CANVAS", bg_color=ColorPalette.BACKGROUND))
    widgets.add(Button(3, 1, "⚡", "FAST", bg_color=ColorPalette.BACKGROUND))

    # Statut
    widgets.add(Button(0, 2, "📊", "READY", bg_color=ColorPalette.SUCCESS))
    widgets.add(Button(4, 2, "ℹ️", "INFO", bg_color=ColorPalette.PRIMARY))

    # 4. Rendu
    print("\n🎨 Rendu de l'interface...")
    canvas.clear(ColorPalette.BACKGROUND)
    widgets.render_all(canvas)
    renderer.update()

    print("✅ Interface rendue avec succès!")

    if hasattr(renderer, 'deck') and renderer.deck is not None:
        print(f"📱 Appareil réel: {renderer.deck.deck_type()}")
        print("   L'interface est affichée sur votre Stream Deck!")
        print("   Pressez Ctrl+C pour quitter.")
    else:
        print("🐛 Mode debug: image sauvegardée")
        print("   Regardez le fichier debug_frame_0000.png")

    # 5. Nettoyage (optionnel en mode debug)
    try:
        if hasattr(renderer, 'deck') and renderer.deck is not None:
            import time
            time.sleep(5)  # Laisser l'interface visible 5 secondes
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")


if __name__ == "__main__":
    main()