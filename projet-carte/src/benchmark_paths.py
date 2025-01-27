from benchmark import BenchmarkAnalyzer
from graph_data import GRAPH_DATA
import os

def run_benchmarks(generate_graphs=True):
    """
    Exécute les benchmarks pour tous les jeux de données définis dans GRAPH_DATA
    """
    print("\nDémarrage des benchmarks...")
    
    for data in GRAPH_DATA:
        print(f"\n{'='*50}")
        print(f"BENCHMARK POUR {data['name'].upper()}")
        print('='*50)
        
        # Vérification de l'existence des fichiers
        if not os.path.exists(data['nodes']) or not os.path.exists(data['ways']):
            print(f"Erreur : Fichiers manquants pour {data['name']}")
            continue
            
        # Création de l'analyseur
        analyzer = BenchmarkAnalyzer(data['nodes'], data['ways'], generate_graphs=generate_graphs)
        
        # Chargement du graphe
        load_time = analyzer.load_graph()
        print(f"Temps de chargement du graphe : {load_time:.3f} secondes")
        
        # Test pour chaque point d'arrivée
        for end_point in data['points']['end']:
            print(f"\nAnalyse du trajet : {data['points']['start']} → {end_point}")
            print('-' * 40)
            
            try:
                results = analyzer.run_comparison(
                    data['points']['start'],
                    end_point,
                    num_runs=5
                )
                
                analyzer.print_results()
                
            except Exception as e:
                print(f"Erreur lors du benchmark : {str(e)}")

def main():
    """Point d'entrée principal"""
    # Exécution des benchmarks avec génération des graphiques
    run_benchmarks(generate_graphs=True)
    
    print("\nBenchmarks terminés !")
    print("Les graphiques ont été générés dans le dossier courant.")

if __name__ == "__main__":
    main()