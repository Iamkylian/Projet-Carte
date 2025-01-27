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
    """Classe pour analyser et comparer les performances des algorithmes de recherche de chemin.
    
    Cette classe permet de :
    - Charger et analyser un graphe à partir de fichiers CSV
    - Comparer les performances de Dijkstra et A*
    - Générer des graphiques de comparaison
    - Mesurer l'utilisation des ressources (temps, mémoire, CPU)
    
    Attributes:
        nodes_file (str): Chemin vers le fichier CSV des nœuds
        ways_file (str): Chemin vers le fichier CSV des chemins
        graph_name (str): Nom du graphe pour l'identification
        graph (Graph): Instance du graphe chargé
        generate_graphs (bool): Indique si les graphiques doivent être générés
        output_dir (str): Dossier de sortie pour les graphiques
    """

    def __init__(self, nodes_file, ways_file, graph_name="default", generate_graphs=True, output_dir="./benchmarks"):
        self.nodes_file = nodes_file
        self.ways_file = ways_file
        self.graph_name = graph_name
        self.graph = None
        self.generate_graphs = generate_graphs
        self.output_dir = os.path.join(output_dir, graph_name)
        
        if generate_graphs:
            os.makedirs(self.output_dir, exist_ok=True)
        
    def load_graph(self):
        """Charge le graphe à partir des fichiers CSV"""
        self.graph = Graph()
        start_time = time.time()
        self.graph.load_from_csv(self.nodes_file, self.ways_file)
        return time.time() - start_time
        
    @profile
    def _run_algorithm(self, start_id, end_id, algorithm="dijkstra"):
        """Exécute un algorithme de recherche de chemin et mesure ses performances.
        
        Args:
            start_id (str): Identifiant du point de départ
            end_id (str): Identifiant du point d'arrivée
            algorithm (str): Algorithme à utiliser ('dijkstra' ou 'a_star')
            
        Returns:
            dict: Résultats des mesures de performance
                {
                    'algorithm': nom de l'algorithme,
                    'time': temps d'exécution,
                    'memory': utilisation mémoire (MB),
                    'cpu': utilisation CPU (%),
                    'path_length': nombre de nœuds dans le chemin,
                    'distance': distance totale (km)
                }
        """
        print(f"\n[INFO] 🚀 Démarrage de {algorithm.upper()}")
        print(f"[INFO] 📍 De: {start_id} → Vers: {end_id}")
        print("-"*40)
        
        process = psutil.Process(os.getpid())
        start_mem, start_cpu = process.memory_info().rss, process.cpu_percent()
        
        start_time = time.time()
        distance, path = (self.graph.dijkstra(start_id, end_id) if algorithm == "dijkstra" 
                         else self.graph.a_star(start_id, end_id))
        execution_time = time.time() - start_time
        
        end_mem, end_cpu = process.memory_info().rss, process.cpu_percent()
        
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
        """Compare les performances des algorithmes Dijkstra et A*.
        
        Exécute plusieurs fois chaque algorithme et collecte les statistiques
        de performance pour une comparaison fiable.
        
        Args:
            start_id (str): Identifiant du point de départ
            end_id (str): Identifiant du point d'arrivée
            path_name (str): Nom du chemin pour l'identification
            num_runs (int): Nombre d'exécutions pour chaque algorithme
            
        Returns:
            dict: Résultats comparatifs des deux algorithmes
        """
        self.path_name = path_name
        self.start_id = start_id
        self.end_id = end_id
        
        self.path_output_dir = os.path.join(self.output_dir, path_name)
        if self.generate_graphs:
            os.makedirs(self.path_output_dir, exist_ok=True)
        
        # Initialisation des résultats
        self.results = {algo: {'times': [], 'memory': [], 'cpu': [], 'path_length': 0, 'distance': 0}
                       for algo in ['dijkstra', 'a_star']}
        
        # Exécution multiple des algorithmes
        for i in range(num_runs):
            print(f"\n[INFO] 🔄 Exécution {i + 1}/{num_runs} pour le chemin {self.path_name}")
            print("-"*50)
            for algo in ['dijkstra', 'a_star']:
                print(f"\n[INFO] ⚙️  Algorithme en cours : {algo.upper()}")
                result = self._run_algorithm(start_id, end_id, algo)
                self.results[algo]['times'].append(result['time'])
                self.results[algo]['memory'].append(result['memory'])
                self.results[algo]['cpu'].append(result['cpu'])
                self.results[algo]['path_length'] = result['path_length']
                self.results[algo]['distance'] = result['distance']
        
        # Calcul des moyennes et écarts-types
        for algo in self.results:
            self.results[algo].update({
                'avg_time': np.mean(self.results[algo]['times']),
                'std_time': np.std(self.results[algo]['times']),
                'avg_memory': np.mean(self.results[algo]['memory']),
                'avg_cpu': np.mean(self.results[algo]['cpu'])
            })
        
        if self.generate_graphs:
            self._generate_plots()
        
        return self.results

    def _generate_plots(self):
        """Génère les graphiques individuels de comparaison des performances.
        
        Crée trois graphiques distincts :
        - Temps d'exécution
        - Utilisation mémoire
        - Utilisation CPU
        """
        plt.style.use('default')
        colors = ['#2ecc71', '#e74c3c']
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
        
        metrics = {
            'time': ('Temps d\'exécution moyen', 'Temps (secondes)'),
            'memory': ('Utilisation moyenne de la mémoire', 'Mémoire (MB)'),
            'cpu': ('Utilisation moyenne du CPU', 'CPU (%)')
        }
        
        for metric, (title, ylabel) in metrics.items():
            plt.figure(figsize=(8, 6))
            data = [self.results[algo][f'avg_{metric}'] for algo in ['dijkstra', 'a_star']]
            plt.bar(['Dijkstra', 'A*'], data)
            plt.title(f'{title} - {self.graph_name}\nChemin: {self.path_name}')
            plt.ylabel(ylabel)
            plt.savefig(os.path.join(self.path_output_dir, f'{self.graph_name}_{self.path_name}_{metric}.png'))
            plt.close()
        
        self._plot_combined_metrics()

    def _plot_combined_metrics(self):
        """Génère un graphique combiné des trois métriques de performance.
        
        Affiche sur une même figure :
        - Temps d'exécution moyen
        - Utilisation moyenne de la mémoire
        - Utilisation moyenne du CPU
        """
        fig, axes = plt.subplots(1, 3, figsize=(15, 6))
        metrics = [('time', 'Temps moyen (s)'), ('memory', 'Mémoire moyenne (MB)'), ('cpu', 'CPU moyen (%)')]
        
        title = (f'Comparaison des performances - {self.graph_name}\n'
                f'Chemin: {self.path_name} (moyenne sur {len(self.results["dijkstra"]["times"])} exécutions)\n'
                f'Nœuds parcourus - Dijkstra: {self.results["dijkstra"]["path_length"]}, '
                f'A*: {self.results["a_star"]["path_length"]}\n'
                f'Distance totale: {self.results["dijkstra"]["distance"]:.2f} km')
        
        fig.suptitle(title, fontsize=10)
        
        for ax, (metric, ylabel) in zip(axes, metrics):
            data = [self.results[algo][f'avg_{metric}'] for algo in ['dijkstra', 'a_star']]
            ax.bar(['Dijkstra', 'A*'], data, color=['#2ecc71', '#e74c3c'])
            ax.set_ylabel(ylabel)
            ax.set_title(metric.capitalize())
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.path_output_dir, f'{self.graph_name}_{self.path_name}_combined_metrics.png'))
        plt.close()

    def print_results(self):
        """Affiche les résultats détaillés des benchmarks dans la console."""
        print("\n" + "="*80)
        print(f" 📊 RÉSULTATS DES BENCHMARKS - {self.graph_name.upper()} - {self.path_name.upper()}")
        print("="*80)

        for algo, results in self.results.items():
            print(f"\n[INFO] 🔍 Analyse de l'algorithme {algo.upper()}")
            print("-"*50)
            print(f"📈 Temps moyen     : {results['avg_time']:.4f} s (±{results['std_time']:.4f})")
            print(f"💾 Mémoire         : {results['avg_memory']:.2f} MB")
            print(f"⚡ CPU             : {results['avg_cpu']:.1f}%")
            print(f"📏 Distance totale : {results['distance']:.2f} km")
            print(f"🔢 Nœuds parcourus : {results['path_length']}")

def main():
    """
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
    """

if __name__ == "__main__":
    main()