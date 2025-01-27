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
import sys

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
    def benchmark_algorithm(self, start_id, end_id, algorithm="dijkstra"):
        """Exécute l'algorithme spécifié et mesure les performances"""
        print(f"\nExécution de l'algorithme : {algorithm.upper()}")
        print("-" * 40)
        
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
        
        execution_time = end_time - start_time
        memory_usage = (end_mem - start_mem) / (1024 * 1024)  # Conversion en MB
        cpu_usage = (end_cpu + start_cpu) / 2
        
        return {
            'algorithm': algorithm,
            'time': execution_time,
            'memory': memory_usage,
            'cpu': cpu_usage,
            'path_length': len(path) if path else 0,
            'distance': distance
        }

    def run_comparison(self, start_id, end_id, path_name="default", num_runs=10):
        """Compare les performances de Dijkstra et A*"""
        self.path_name = path_name
        self.start_id = start_id
        self.end_id = end_id
        
        self.path_output_dir = os.path.join(self.output_dir, path_name)
        if self.generate_graphs:
            os.makedirs(self.path_output_dir, exist_ok=True)
        
        # Initialisation des résultats
        self.results = {
            'dijkstra': {'times': [], 'memory': [], 'cpu': [], 'path_length': 0, 'distance': 0},
            'a_star': {'times': [], 'memory': [], 'cpu': [], 'path_length': 0, 'distance': 0}
        }
        
        # Exécution multiple des algorithmes
        for _ in range(num_runs):
            # Dijkstra
            d_result = self.benchmark_algorithm(start_id, end_id, "dijkstra")
            self.results['dijkstra']['times'].append(d_result['time'])
            self.results['dijkstra']['memory'].append(d_result['memory'])
            self.results['dijkstra']['cpu'].append(d_result['cpu'])
            self.results['dijkstra']['path_length'] = d_result['path_length']
            self.results['dijkstra']['distance'] = d_result['distance']
            
            # A*
            a_result = self.benchmark_algorithm(start_id, end_id, "a_star")
            self.results['a_star']['times'].append(a_result['time'])
            self.results['a_star']['memory'].append(a_result['memory'])
            self.results['a_star']['cpu'].append(a_result['cpu'])
            self.results['a_star']['path_length'] = a_result['path_length']
            self.results['a_star']['distance'] = a_result['distance']
        
        # Calcul des moyennes et écarts-types
        for algo in ['dijkstra', 'a_star']:
            self.results[algo]['avg_time'] = np.mean(self.results[algo]['times'])
            self.results[algo]['std_time'] = np.std(self.results[algo]['times'])
            self.results[algo]['avg_memory'] = np.mean(self.results[algo]['memory'])
            self.results[algo]['avg_cpu'] = np.mean(self.results[algo]['cpu'])
        
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
        avg_times = [self.results['dijkstra']['avg_time'], self.results['a_star']['avg_time']]
        plt.bar(['Dijkstra', 'A*'], avg_times)
        plt.title(f'Temps d\'exécution moyen - {self.graph_name}\nChemin: {self.path_name}')
        plt.ylabel('Temps (secondes)')
        filename = f'{self.graph_name}_{self.path_name}_execution_times.png'
        plt.savefig(os.path.join(self.path_output_dir, filename))
        plt.close()

    def _plot_memory_usage(self):
        plt.figure(figsize=(8, 6))
        memory_data = [self.results['dijkstra']['avg_memory'], self.results['a_star']['avg_memory']]
        plt.bar(['Dijkstra', 'A*'], memory_data)
        plt.title(f'Utilisation moyenne de la mémoire - {self.graph_name}\nChemin: {self.path_name}')
        plt.ylabel('Mémoire (MB)')
        filename = f'{self.graph_name}_{self.path_name}_memory_usage.png'
        plt.savefig(os.path.join(self.path_output_dir, filename))
        plt.close()

    def _plot_cpu_usage(self):
        plt.figure(figsize=(8, 6))
        cpu_data = [self.results['dijkstra']['avg_cpu'], self.results['a_star']['avg_cpu']]
        plt.bar(['Dijkstra', 'A*'], cpu_data)
        plt.title(f'Utilisation moyenne du CPU - {self.graph_name}\nChemin: {self.path_name}')
        plt.ylabel('CPU (%)')
        filename = f'{self.graph_name}_{self.path_name}_cpu_usage.png'
        plt.savefig(os.path.join(self.path_output_dir, filename))
        plt.close()

    def _plot_combined_metrics(self):
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 6))
        
        # Calcul des moyennes pour les deux algorithmes
        dijkstra_nodes = self.results['dijkstra']['path_length']
        astar_nodes = self.results['a_star']['path_length']
        dijkstra_distance = self.results['dijkstra']['distance']
        astar_distance = self.results['a_star']['distance']
        
        # Création du titre avec les informations supplémentaires
        title = (f'Comparaison des performances - {self.graph_name}\n'
                f'Chemin: {self.path_name} (moyenne sur {len(self.results["dijkstra"]["times"])} exécutions)\n'
                f'Nœuds parcourus - Dijkstra: {dijkstra_nodes}, A*: {astar_nodes}\n'
                f'Distance totale: {dijkstra_distance:.2f} km')
        
        fig.suptitle(title, fontsize=10)
        
        # Configuration des couleurs
        colors = ['#2ecc71', '#e74c3c']  # Vert et rouge
        
        # Temps d'exécution (axe 1)
        times = [self.results['dijkstra']['avg_time'], self.results['a_star']['avg_time']]
        ax1.bar(['Dijkstra', 'A*'], times, color=colors)
        ax1.set_ylabel('Temps moyen (s)')
        ax1.set_title('Temps d\'exécution')
        
        # Mémoire (axe 2)
        memory = [self.results['dijkstra']['avg_memory'], self.results['a_star']['avg_memory']]
        ax2.bar(['Dijkstra', 'A*'], memory, color=colors)
        ax2.set_ylabel('Mémoire moyenne (MB)')
        ax2.set_title('Utilisation mémoire')
        
        # CPU (axe 3)
        cpu = [self.results['dijkstra']['avg_cpu'], self.results['a_star']['avg_cpu']]
        ax3.bar(['Dijkstra', 'A*'], cpu, color=colors)
        ax3.set_ylabel('CPU moyen (%)')
        ax3.set_title('Utilisation CPU')
        
        plt.tight_layout()
        
        filename = f'{self.graph_name}_{self.path_name}_combined_metrics.png'
        plt.savefig(os.path.join(self.path_output_dir, filename))
        plt.close()

    def print_results(self):
        """Affiche les résultats des benchmarks"""
        for algo, results in self.results.items():
            print(f"\nRésultats pour {algo.upper()} (moyenne sur {len(results['times'])} exécutions):")
            print(f"Temps moyen: {results['avg_time']:.4f} s (±{results['std_time']:.4f})")
            print(f"Utilisation mémoire: {results['avg_memory']:.2f} MB")
            print(f"Utilisation CPU: {results['avg_cpu']:.1f}%")
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