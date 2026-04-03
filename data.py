# Génère les données histoiques d'achalandage pour la ligne orange de la STM

import os
import pandas as pd
def create_stm_data():

    #Vérifie si le fichier CSV existe déjà
    if os.path.exists('stm_orange_line.csv'):
        return
    #Si le ficihier n'existe, crée un dictinnaire contenant les stations, les temps de transit et le nombre de passager qui montent ou descendent.
    dataset = {
        'Station':[
            'Côte-Vertu', 'Du Collège', 'De La Savane', 'Namur', 'Plamondon',
            'Côte-Sainte-Catherine', 'Snowdon', 'Villa-Maria', 'Vendôme', 'Place-Saint-Henri',
            'Lionel-Groulx', 'Georges-Vanier', "Lucien-L'Allier", 'Bonaventure',
            'Square-Victoria-OACI', "Place-d'Armes", 'Champ-de-Mars', 'Berri-UQAM',
            'Sherbrooke', 'Mont-Royal', 'Laurier', 'Rosemont', 'Beaubien', 'Jean-Talon',
            'Jarry', 'Crémazie', 'Sauvé', 'Henri-Bourassa', 'Cartier', 'De La Concorde', 'Montmorency'
        ],
        'transit_time_sec':[
            66, 92, 65, 76, 46, 60, 70, 103, 103, 55, 64, 53, 49, 43, 43, 43, 
            84, 56, 74, 53, 63, 52, 61, 76, 67, 99, 94, 86, 132, 96, 0
        ],
        'boarding_on_AM':[1200, 750, 375, 450, 675, 825, 975, 450, 900, 375, 1350, 225, 450, 675, 900, 450, 225, 1200, 675, 750, 450, 675, 750, 975, 450, 450, 750, 1050, 755, 375, 150],
        'boarding_off_AM':[0, 225, 150, 225, 375, 450, 675, 225, 675, 225, 900, 150, 900, 1350, 1200, 675, 375, 900, 375, 450, 375, 375, 450, 675, 375, 375, 450, 450, 63, 150, 750],
        'boarding_off_peak':[300, 225, 120, 150, 180, 225, 300, 150, 270, 120, 375, 75, 150, 225, 300, 150, 75, 375, 180, 225, 150, 180, 225, 300, 150, 150, 225, 300, 129, 120, 75],
        'descending_off_peak':[0, 75, 60, 75, 120, 150, 225, 75, 225, 75, 300, 45, 300, 450, 375, 225, 120, 300, 120, 150, 120, 120, 150, 225, 120, 120, 150, 150, 94, 60, 225]
    }


    # Utilise la biliothèque Pandas pour convertir le dictionnaire et le sauvegarder en stm_orange_line.csv
    pd.DataFrame(dataset).to_csv('stm_orange_line.csv', index=False)

    