#lance l'application en important la bilbliotèque Tkinter, crée la fenêtre principale et instansie la classe SimApp et lance la boucle d'événements.
import tkinter as tk
from gui import SimApp
if __name__ == '__main__':
    root = tk.Tk()
    app = SimApp(root)
    root.mainloop()