"""
Outil CLI pour générer des nouveaux widgets
"""

import sys
import os

TEMPLATE = """from streamdeck_canvas.framework import SimpleWidget
from streamdeck_canvas import ColorPalette
import math

class {class_name}(SimpleWidget):
    """
    Nouveau composant : {class_name}
    """
    
    def setup(self):
        # Initialisez vos variables ici
        # self.color est disponible si passé dans le constructeur
        self.counter = 0.0
        if not hasattr(self, 'color'):
            self.color = '#FFFFFF'

    def on_update(self, dt):
        # Logique d'animation (dt = temps écoulé depuis la dernière frame en secondes)
        self.counter += dt

    def on_draw(self, canvas):
        # Récupérer les dimensions
        x, y, w, h = canvas.get_region_rect(self.col, self.row, self.width, self.height)
        
        # Exemple : Rectangle qui change de taille
        scale = (math.sin(self.counter * 3) + 1) / 2 # 0.0 à 1.0
        radius = int(10 * scale)
        
        # Dessiner
        canvas.draw_rect(
            self.col, self.row, 
            width_cols=self.width, 
            height_rows=self.height,
            color=self.color,
            radius=radius
        )
        
        # Texte
        canvas.draw_text(
            self.col, self.row, 
            text=f"{self.counter:.1f}}s",
            color='#000000',
            align='center'
        )
"""

def create_widget_file(name: str):
    filename = f"{name.lower()}.py"
    class_name = name.capitalize()
    
    if os.path.exists(filename):
        print(f"❌ Erreur: Le fichier {filename} existe déjà.")
        return

    content = TEMPLATE.format(class_name=class_name)
    
    with open(filename, "w") as f:
        f.write(content)
        
    print(f"✅ Widget créé : {filename}")
    print(f"👉 Utilisation :")
    print(f"   from {name.lower()} import {class_name}")
    print(f"   widgets.add({class_name}(0, 0, width=1, color='#FF0000'))")

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m streamdeck_canvas.cli create <WidgetName>")
        return

    command = sys.argv[1]
    
    if command == "create" and len(sys.argv) == 3:
        create_widget_file(sys.argv[2])
    else:
        print("Commande inconnue.")

if __name__ == "__main__":
    main()
