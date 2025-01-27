import time
import matplotlib.pyplot as plt
import numpy as np
from graph import Graph
import os
import psutil
import cProfile
import pstats
from memory_profiler import profile
import seaborn as sns

class BenchmarkAnalyzer:
    def __init__(self, nodes_file, ways_file, graph_name="default", generate_graphs=True, output_dir="./benchmarks"):
        self.nodes_file = nodes_file
        self.ways_file = ways_file
        self.graph_name = graph_name
        self.graph = None
        self.generate_graphs = generate_graphs
        self.results = {}
        self.output_dir = os.path.join(output_dir, graph_name)
        
        if generate_graphs:
            os.makedirs(self.output_dir, exist_ok=True)
        
    def load_graph(self):
        """Charge le graphe à partir des fichiers CSV"""
        self.graph = Graph()
        start_time = time.time()
        self.graph.load_from_csv(self.nodes_file, self.ways_file)
        load_time = time.time() - start_time
        return load_time
        
    @profile
    def benchmark_algorithm(self, start_id, end_id, algorithm="dijkstra", num_runs=5):
        """Exécute l'algorithme spécifié plusieurs fois et mesure les performances"""
        times = []
        memory_usage = []
        cpu_usage = []
        
        for _ in range(num_runs):
            process = psutil.Process(os.getpid())
            start_mem = process.memory_info().rss
            
            start_time = time.time()
            start_cpu = process.cpu_percent()
            
            if algorithm == "dijkstra":
                distance, path = self.graph.dijkstra(start_id, end_id)
            else:
                distance, path = self.graph.a_star(start_id, end_id)
            
            end_time = time.time()
            end_cpu = process.cpu_percent()
            end_mem = process.memory_info().rss
            
            times.append(end_time - start_time)
            memory_usage.append((end_mem - start_mem) / (1024 * 1024))  # Conversion en MB
            cpu_usage.append((end_cpu + start_cpu) / 2)
            
        return {
            'algorithm': algorithm,
            'times': times,
            'avg_time': np.mean(times),
            'std_time': np.std(times),
            'memory': np.mean(memory_usage),
            'cpu': np.mean(cpu_usage),
            'path_length': len(path) if path else 0,
            'distance': distance
        }

    def run_comparison(self, start_id, end_id, num_runs=5):
        """Compare les performances de Dijkstra et A*"""
        self.results['dijkstra'] = self.benchmark_algorithm(start_id, end_id, "dijkstra", num_runs)
        self.results['a_star'] = self.benchmark_algorithm(start_id, end_id, "a_star", num_runs)
        
        if self.generate_graphs:
            self.generate_comparison_graphs()
        
        return self.results

    def generate_comparison_graphs(self):
        """Génère des graphiques comparatifs"""
        # Configuration du style
        plt.style.use('default')  # Utilisation du style par défaut de matplotlib
        
        # Configuration des couleurs
        colors = ['#2ecc71', '#e74c3c']  # Vert et rouge
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

        # 1. Temps d'exécution
        self._plot_execution_times()
        
        # 2. Utilisation mémoire
        self._plot_memory_usage()
        
        # 3. Utilisation CPU
        self._plot_cpu_usage()
        
        # 4. Graphique combiné
        self._plot_combined_metrics()

    def _plot_execution_times(self):
        plt.figure(figsize=(10, 6))
        avg_times = [np.mean(self.results['dijkstra']['times']), 
                    np.mean(self.results['a_star']['times'])]
        plt.bar(['Dijkstra', 'A*'], avg_times)
        plt.title(f'Temps d\'exécution moyen - {self.graph_name}')
        plt.ylabel('Temps (secondes)')
        plt.savefig(os.path.join(self.output_dir, f'{self.graph_name}_execution_times.png'))
        plt.close()

    def _plot_memory_usage(self):
        plt.figure(figsize=(8, 6))
        memory_data = [self.results['dijkstra']['memory'], self.results['a_star']['memory']]
        plt.bar(['Dijkstra', 'A*'], memory_data)
        plt.title(f'Utilisation moyenne de la mémoire - {self.graph_name}')
        plt.ylabel('Mémoire (MB)')
        plt.savefig(os.path.join(self.output_dir, f'{self.graph_name}_memory_usage.png'))
        plt.close()

    def _plot_cpu_usage(self):
        plt.figure(figsize=(8, 6))
        cpu_data = [self.results['dijkstra']['cpu'], self.results['a_star']['cpu']]
        plt.bar(['Dijkstra', 'A*'], cpu_data)
        plt.title(f'Utilisation moyenne du CPU - {self.graph_name}')
        plt.ylabel('CPU (%)')
        plt.savefig(os.path.join(self.output_dir, f'{self.graph_name}_cpu_usage.png'))
        plt.close()

    def _plot_combined_metrics(self):
        plt.figure(figsize=(12, 8))
        metrics = ['avg_time', 'memory', 'cpu']
        labels = ['Temps (s)', 'Mémoire (MB)', 'CPU (%)']
        
        x = np.arange(len(metrics))
        width = 0.35
        
        dijkstra_values = [self.results['dijkstra'][m] for m in metrics]
        astar_values = [self.results['a_star'][m] for m in metrics]
        
        plt.bar(x - width/2, dijkstra_values, width, label='Dijkstra')
        plt.bar(x + width/2, astar_values, width, label='A*')
        
        plt.xlabel('Métrique')
        plt.ylabel('Valeur')
        plt.title(f'Comparaison des performances - {self.graph_name}')
        plt.xticks(x, labels)
        plt.legend()
        
        plt.savefig(os.path.join(self.output_dir, f'{self.graph_name}_combined_metrics.png'))
        plt.close()

    def print_results(self):
        """Affiche les résultats des benchmarks"""
        for algo, results in self.results.items():
            print(f"\nRésultats pour {algo.upper()}:")
            print(f"Temps moyen: {results['avg_time']:.4f} s (±{results['std_time']:.4f})")
            print(f"Utilisation mémoire: {results['memory']:.2f} MB")
            print(f"Utilisation CPU: {results['cpu']:.1f}%")
            print(f"Longueur du chemin: {results['path_length']} nœuds")
            print(f"Distance totale: {results['distance']:.2f} km")

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
        results[desc] = analyzer.run_comparison(start_id, end_id)
        analyzer.print_results()
        
        # Profile l'algorithme
        print(f"\nProfiling pour {desc}:")
        stats = analyzer.profile_algorithm(start_id, end_id)
        stats.print_stats(10)  # Affiche les 10 fonctions les plus coûteuses

if __name__ == "__main__":
    main()