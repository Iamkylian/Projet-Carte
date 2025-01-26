import time
import matplotlib.pyplot as plt
import numpy as np
from graph import Graph
import os
import psutil
import cProfile
import pstats
from memory_profiler import profile

class BenchmarkAnalyzer:
    def __init__(self, nodes_file, ways_file):
        self.nodes_file = nodes_file
        self.ways_file = ways_file
        self.graph = None
        
    def load_graph(self):
        """Charge le graphe à partir des fichiers CSV"""
        self.graph = Graph()
        self.graph.load_from_csv(self.nodes_file, self.ways_file)
        
    @profile
    def run_dijkstra_benchmark(self, start_id, end_id, num_runs=5):
        """Exécute l'algorithme de Dijkstra plusieurs fois et mesure les performances"""
        times = []
        memory_usage = []
        cpu_usage = []
        
        for _ in range(num_runs):
            process = psutil.Process(os.getpid())
            start_mem = process.memory_info().rss
            
            start_time = time.time()
            start_cpu = process.cpu_percent()
            
            distance, path = self.graph.dijkstra(start_id, end_id)
            
            end_time = time.time()
            end_cpu = process.cpu_percent()
            end_mem = process.memory_info().rss
            
            times.append(end_time - start_time)
            memory_usage.append(end_mem - start_mem)
            cpu_usage.append((end_cpu + start_cpu) / 2)
            
        return {
            'times': times,
            'avg_time': np.mean(times),
            'std_time': np.std(times),
            'memory': np.mean(memory_usage),
            'cpu': np.mean(cpu_usage)
        }

    def profile_algorithm(self, start_id, end_id):
        """Profile l'algorithme avec cProfile"""
        profiler = cProfile.Profile()
        profiler.enable()
        self.graph.dijkstra(start_id, end_id)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        return stats

    def plot_results(self, results, title):
        """Génère un graphique des résultats"""
        plt.figure(figsize=(10, 6))
        plt.boxplot(results['times'])
        plt.title(f'Distribution des temps d\'exécution - {title}')
        plt.ylabel('Temps (secondes)')
        plt.savefig(f'benchmark_{title.lower().replace(" ", "_")}.png')
        plt.close()

def main():
    # Chemins des fichiers
    nodes_file = "./../data/france/serres-sur-arget/osm_nodes.csv"
    ways_file = "./../data/france/serres-sur-arget/osm_ways.csv"
    
    # Points de test
    test_cases = [
        ("469819297", "1792742726", "Court trajet"), # Saint-Pierre-de-Rivière -> Los Prados
        ("469819297", "1205464576", "Moyen trajet"), # Saint-Pierre-de-Rivière -> Cabane Coumauzil
    ]
    
    analyzer = BenchmarkAnalyzer(nodes_file, ways_file)
    analyzer.load_graph()
    
    results = {}
    for start_id, end_id, desc in test_cases:
        print(f"\nExécution des benchmarks pour {desc}...")
        results[desc] = analyzer.run_dijkstra_benchmark(start_id, end_id)
        analyzer.plot_results(results[desc], desc)
        
        print(f"\nRésultats pour {desc}:")
        print(f"Temps moyen: {results[desc]['avg_time']:.4f} s")
        print(f"Écart-type: {results[desc]['std_time']:.4f} s")
        print(f"Utilisation mémoire moyenne: {results[desc]['memory'] / 1024 / 1024:.2f} MB")
        print(f"Utilisation CPU moyenne: {results[desc]['cpu']:.1f}%")
        
        # Profile l'algorithme
        print(f"\nProfiling pour {desc}:")
        stats = analyzer.profile_algorithm(start_id, end_id)
        stats.print_stats(10)  # Affiche les 10 fonctions les plus coûteuses

if __name__ == "__main__":
    main()