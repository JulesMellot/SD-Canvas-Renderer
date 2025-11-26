#!/usr/bin/env python3
"""
Stream Deck Device Detection
Script pour détecter et afficher les informations des Stream Deck connectés
"""

try:
    from StreamDeck.DeviceManager import DeviceManager
    STREAMDECK_AVAILABLE = True
except ImportError:
    print("❌ Librairie StreamDeck non trouvée!")
    print("   Installez avec: pip install StreamDeck")
    STREAMDECK_AVAILABLE = False
    exit(1)


def print_deck_info(index, deck):
    """Affiche les informations détaillées d'un Stream Deck"""

    key_image_format = deck.key_image_format()

    flip_description = {
        (False, False): "non miroir",
        (True, False): "miroir horizontal",
        (False, True): "miroir vertical",
        (True, True): "miroir horizontal/vertical",
    }

    print(f"📱 Stream Deck #{index + 1}")
    print(f"   Modèle: {deck.deck_type()}")
    print(f"   ID: {deck.id()}")
    print(f"   Numéro de série: {deck.get_serial_number()}")
    print(f"   Firmware: {deck.get_firmware_version()}")
    print(f"   Grille: {deck.key_layout()[0]}×{deck.key_layout()[1]} ({deck.key_count()} touches)")

    if deck.is_visual():
        print(f"   Images: {key_image_format['size'][0]}×{key_image_format['size'][1]} pixels")
        print(f"   Format: {key_image_format['format']}")
        print(f"   Rotation: {key_image_format['rotation']}°")
        print(f"   Miroir: {flip_description[key_image_format['flip']]}")

        if deck.is_touch():
            touchscreen = deck.touchscreen_image_format()
            print(f"   📱 Touchscreen: {touchscreen['size'][0]}×{touchscreen['size'][1]} pixels")
        else:
            print(f"   📱 Touchscreen: Non")
    else:
        print(f"   🖼️  Sortie visuelle: Non")

    # Vérifier la compatibilité avec notre renderer
    cols, rows = deck.key_layout()
    size = key_image_format['size'][0]

    print(f"   ✅ Compatible avec StreamDeckCanvasRenderer:")
    print(f"      → Canvas: {cols}×{rows} boutons")
    print(f"      → Taille: {size}px par bouton")
    print(f"      → Canvas total: {cols * size}×{rows * size} pixels")

    return cols, rows, size


def main():
    """Détecte et affiche tous les Stream Deck connectés"""

    print("🔍 Recherche de Stream Decks...")
    print("=" * 50)

    # Énumérer les appareils
    streamdecks = DeviceManager().enumerate()

    if not streamdecks:
        print("❌ Aucun Stream Deck trouvé!")
        print("\n💡 Dépannage:")
        print("   • Vérifiez que l'appareil est connecté via USB")
        print("   • Assurez-vous que les câbles sont bien branchés")
        print("   • Sur macOS/Linux, vérifiez les permissions USB")
        print("   • Essayez de débrancher/rebrancher l'appareil")
        print("   • Redémarrez l'appareil si nécessaire")
        return

    print(f"✅ {len(streamdecks)} Stream Deck(s) trouvé(s)")
    print("=" * 50)

    all_decks = []

    for index, deck in enumerate(streamdecks):
        try:
            deck.open()
            deck.reset()

            cols, rows, size = print_deck_info(index, deck)
            all_decks.append({
                'deck': deck,
                'cols': cols,
                'rows': rows,
                'size': size,
                'index': index
            })

            deck.close()
            print()

        except Exception as e:
            print(f"❌ Erreur avec le Stream Deck #{index + 1}: {e}")
            print()

    # Résumé pour le développeur
    print("🎯 Résumé pour StreamDeckCanvasRenderer:")
    print("=" * 50)

    for i, deck_info in enumerate(all_decks):
        cols, rows, size = deck_info['cols'], deck_info['rows'], deck_info['size']
        print(f"Appareil #{i + 1}:")
        print(f"   renderer = DebugRenderer(cols={cols}, rows={rows}, button_size={size})")
        print(f"   # ou avec appareil réel:")
        print(f"   # renderer = StreamDeckRenderer(deck)")

    if all_decks:
        print("\n🚀 Pour tester avec le premier appareil:")
        print(f"   python examples/real_device.py")

        print("\n🧪 Pour tester en mode debug:")
        if len(all_decks) > 0:
            first = all_decks[0]
            print(f"   python -c \"from streamdeck_canvas import DebugRenderer; r=DebugRenderer(cols={first['cols']}, rows={first['rows']}, button_size={first['size']}); print('✅ Debug renderer prêt!')\"")


if __name__ == "__main__":
    main()