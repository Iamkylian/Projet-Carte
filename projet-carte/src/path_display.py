import time
import io
import cProfile
import pstats
from graph import Graph
from graph_data import GRAPH_DATA

def display_path_results():
    """Affiche les résultats des chemins pour chaque graphe."""
    for data in GRAPH_DATA:
        print(f"\n{'='*50}")
        print(f"RÉSULTATS POUR LE GRAPHE DE {data['name'].upper()}")
        print('='*50)
        
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
    display_path_results()