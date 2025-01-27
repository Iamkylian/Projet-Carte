from benchmark import BenchmarkAnalyzer
from graph_data import GRAPH_DATA
import os

def run_benchmarks(generate_graphs=True):
    """
    Exécute les benchmarks pour tous les jeux de données définis dans GRAPH_DATA
    """
    print("\nDémarrage des benchmarks...")
    
    for data in GRAPH_DATA:
        print(f"\nAnalyse du graphe : {data['name']}")
        analyzer = BenchmarkAnalyzer(
            data['nodes'], 
            data['ways'],
            graph_name=data['name'],
            generate_graphs=generate_graphs
        )
        analyzer.load_graph()
        
        for end_point in data['points']['end']:
            print(f"\nAnalyse du trajet : {data['points']['start']} → {end_point}")
            results = analyzer.run_comparison(data['points']['start'], end_point)
            analyzer.print_results()

def main():
    """Point d'entrée principal"""
    # Exécution des benchmarks avec génération des graphiques
    run_benchmarks(generate_graphs=True)
    
    print("\nBenchmarks terminés !")
    print("Les graphiques ont été générés dans le dossier courant.")

if __name__ == "__main__":
    main()