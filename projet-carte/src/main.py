import cProfile
import pstats
from graph import Graph
import io
import time  # Ajout de l'import time

def main():
    """[OLD] Point d'entrée du programme."""
    # Définition des chemins de fichiers dans un dictionnaire
    graph_data = [
        {
            "name": "Serres-sur-Arget",
            "nodes": "./../data/france/serres-sur-arget/osm_nodes.csv",
            "ways": "./../data/france/serres-sur-arget/osm_ways.csv",
            "points": {
                "start": "469819297",    # Saint-Pierre-de-Rivière
                "end": ["1792742726", "1205464576", "8490363670"]  # Las Prados, Cabane Coumauzil - barguillere, Grotte Bernard
            }
        },
        {
            "name": "Ariège",
            "nodes": "./../data/france/ariege/osm_nodes.csv",
            "ways": "./../data/france/ariege/osm_ways.csv",
            "points": {
                "start": "469819297", # Saint-Pierre-de-Rivière
                "end": ["1792742726", "8490363670"] # Las Prados, Grotte Bernard
            }
        },
        # {
        #     "name": "Midi-Pyrénées",
        #     "nodes": "./../data/france/midipyr/osm_nodes.csv",
        #     "ways": "./../data/france/midipyr/osm_ways.csv",
        #     "points": {
        #         "start": "469819297",
        #         "end": ["1792742726", "8490363670"] # Las Prados, Grotte Bernard
        #     }
        # }
    ]

    # Chargement et traitement pour chaque graphe
    for data in graph_data:
        print(f"\n{'='*50}")
        print(f"RÉSULTATS POUR LE GRAPHE DE {data['name'].upper()}")
        print('='*50)
        
        # Création et chargement du graphe avec mesure du temps
        g = Graph()
        try:
            debut_chargement = time.time()
            g.load_from_csv(data['nodes'], data['ways'])
            fin_chargement = time.time()
            temps_chargement = fin_chargement - debut_chargement
            
            print(f"Graphe de {data['name']} chargé avec succès")
            print(f"Temps de chargement : {temps_chargement:.3f} secondes")
            
            # Pour chaque point d'arrivée
            for end_point in data['points']['end']:
                print(f"\nCalcul du chemin de {data['points']['start']} vers le point {end_point}")
                print('-'*30)
                
                # Dijkstra
                pr_dijkstra = cProfile.Profile()
                pr_dijkstra.enable()
                distance_dijkstra, path_dijkstra = g.dijkstra(data['points']['start'], end_point)
                pr_dijkstra.disable()
                
                # A*
                pr_astar = cProfile.Profile()
                pr_astar.enable()
                distance_astar, path_astar = g.a_star(data['points']['start'], end_point)
                pr_astar.disable()
                
                # Calcul des temps d'exécution
                s_dijkstra = io.StringIO()
                s_astar = io.StringIO()
                ps_dijkstra = pstats.Stats(pr_dijkstra, stream=s_dijkstra)
                ps_astar = pstats.Stats(pr_astar, stream=s_astar)
                
                # Affichage des résultats
                print("\nAlgorithme de Dijkstra :")
                print("-"*20)
                if path_dijkstra:
                    g.print_path(path_dijkstra, distance_dijkstra)
                    print(f"Temps d'exécution : {ps_dijkstra.total_tt:.3f} secondes")
                else:
                    print("Aucun chemin trouvé")
                
                print("\nAlgorithme A* :")
                print("-"*20)
                if path_astar:
                    g.print_path(path_astar, distance_astar)
                    print(f"Temps d'exécution : {ps_astar.total_tt:.3f} secondes")
                else:
                    print("Aucun chemin trouvé")
                
                start_id = data['points']['start']
                end_id = end_point
                if start_id not in g.nodes:
                    print(f"Point de départ {start_id} non trouvé dans le graphe")
                if end_id not in g.nodes:
                    print(f"Point d'arrivée {end_id} non trouvé dans le graphe")
                
        except Exception as e:
            print(f"Erreur lors du chargement du graphe de {data['name']}: {str(e)}")

if __name__ == "__main__":
    main()