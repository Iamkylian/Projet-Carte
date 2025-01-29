import csv
import pandas as pd
import polars as pl
import time
from graph import Graph

class GraphCSV(Graph):
    def load_from_csv(self, nodes_file, ways_file):
        """Charge les données avec le module CSV standard.
        
        Args:
            nodes_file (str): Chemin vers le fichier des nœuds
            ways_file (str): Chemin vers le fichier des routes
        """
        start_time = time.time()

        with open(nodes_file, "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:

                self.add_node(row["id"], float(row["lat"]), float(row["lon"]), row["name"])

        with open(ways_file, "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.add_edge(row["node_from"], row["node_to"], float(row["distance_km"]))
        
        end_time = time.time()
        print(f"Chargement du fichier CSV avec le module python 'csv' terminé en {end_time - start_time:.2f} s.")
                


class GraphPandas(Graph):
    def load_from_csv(self, nodes_file, ways_file):
        """Charge les données avec Pandas.
        
        Args:
            nodes_file (str): Chemin vers le fichier des nœuds
            ways_file (str): Chemin vers le fichier des routes
        """
        start_time = time.time()

        # Lecture des noeuds avec types spécifiés
        df_nodes = pd.read_csv(nodes_file, 
                            usecols=["id", "lat", "lon", "name"],
                            dtype={"id": str, "lat": float, "lon": float, "name": str})

        # Lecture des chemins avec types spécifiés
        df_ways = pd.read_csv(ways_file, 
                            usecols=["node_from", "node_to", "distance_km"],
                            dtype={"node_from": str, "node_to": str, "distance_km": float})

        # Construction du graphe - Noeuds
        for row in df_nodes.itertuples(index=False):
            self.add_node(row.id, row.lat, row.lon, row.name)

        # Construction du graphe - Chemins
        for row in df_ways.itertuples(index=False):
            self.add_edge(row.node_from, row.node_to, row.distance_km)

        end_time = time.time()
        print(f"Chargement du fichier CSV avec le module 'pandas' terminé en {end_time - start_time:.2f} s.")


class GraphPolars(Graph):
    def load_from_csv(self, nodes_file, ways_file):
        """Charge les données avec Polars.
        
        Args:
            nodes_file (str): Chemin vers le fichier des nœuds
            ways_file (str): Chemin vers le fichier des routes
        """
        start_time = time.time()

        # Load nodes with Polars
        nodes_df = pl.read_csv(nodes_file)
        for row in nodes_df.iter_rows():
            # Check for null values
            node_id = str(row[0]) if row[0] is not None else None
            lat = float(row[3]) if row[3] is not None else 0.0
            lon = float(row[2]) if row[2] is not None else 0.0
            name = str(row[1]) if row[1] is not None else ""
            
            if node_id is not None:
                self.add_node(node_id, lat, lon, name)

        # Load ways with Polars
        ways_df = pl.read_csv(ways_file)
        for row in ways_df.iter_rows():
            node1 = str(row[2]) if row[2] is not None else None
            node2 = str(row[3]) if row[3] is not None else None
            distance = float(row[6]) if row[6] is not None else 0.0
            
            if node1 is not None and node2 is not None:
                self.add_edge(node1, node2, distance)

        end_time = time.time()
        print(f"Chargement du fichier CSV avec le module 'polars' terminé en {end_time - start_time:.2f} s.")


def test_load_csv_methods(data_name, nodes_file, ways_file):
    """Teste les trois méthodes de chargement pour un jeu de données.
    
    Args:
        data_name (str): Nom du jeu de données
        nodes_file (str): Chemin vers le fichier des nœuds
        ways_file (str): Chemin vers le fichier des routes
    """
    print(f"\n{'='*50}")
    print(f"TEST DES MÉTHODES DE CHARGEMENT - {data_name.upper()}")
    print('='*50)
    
    results = {}
    
    # Test de la méthode CSV Python
    print("\n1. Test de la méthode CSV Python")
    try:
        start_time = time.time()
        graph_csv = GraphCSV()
        graph_csv.load_from_csv(nodes_file, ways_file)
        csv_time = time.time() - start_time
        print(f"✅ Succès - Temps d'exécution : {csv_time:.3f} secondes")
        print(f"Nombre de nodes : {len(graph_csv.nodes)}")
        # Calcul du nombre total d'arêtes à partir des voisins
        total_edges = sum(len(node.neighbors) for node in graph_csv.nodes.values()) // 2
        print(f"Nombre d'arêtes : {total_edges}")
        results['CSV Python'] = csv_time
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        results['CSV Python'] = None
    
    # Test de la méthode Pandas
    print("\n2. Test de la méthode Pandas")
    try:
        start_time = time.time()
        graph_pandas = GraphPandas()
        graph_pandas.load_from_csv(nodes_file, ways_file)
        pandas_time = time.time() - start_time
        print(f"✅ Succès - Temps d'exécution : {pandas_time:.3f} secondes")
        print(f"Nombre de nodes : {len(graph_pandas.nodes)}")
        total_edges = sum(len(node.neighbors) for node in graph_pandas.nodes.values()) // 2
        print(f"Nombre d'arêtes : {total_edges}")
        results['Pandas'] = pandas_time
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        results['Pandas'] = None
    
    # Test de la méthode Polars
    print("\n3. Test de la méthode Polars")
    try:
        start_time = time.time()
        graph_polars = GraphPolars()
        graph_polars.load_from_csv(nodes_file, ways_file)
        polars_time = time.time() - start_time
        print(f"✅ Succès - Temps d'exécution : {polars_time:.3f} secondes")
        print(f"Nombre de nodes : {len(graph_polars.nodes)}")
        total_edges = sum(len(node.neighbors) for node in graph_polars.nodes.values()) // 2
        print(f"Nombre d'arêtes : {total_edges}")
        results['Polars'] = polars_time
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        results['Polars'] = None
    
    return results

def main():
    """Test des différentes méthodes de chargement pour tous les jeux de données."""
    
    from benchmark import BenchmarkAnalyzer
    from graph_data import GRAPH_DATA
    
    print("\nDémarrage des benchmarks de chargement...")
    
    for data in GRAPH_DATA:
        print(f"\nAnalyse du graphe : {data['name']}")
        analyzer = BenchmarkAnalyzer(
            data['nodes'], 
            data['ways'],
            graph_name=data['name'],
            generate_graphs=True,
            output_dir="./benchmarks/loading_csv_methods"
        )
        
        # Exécution des benchmarks de chargement
        analyzer.benchmark_load_csv_methods()
        
        print(f"\nBenchmarks terminés pour {data['name']}")
        print("Les graphiques ont été générés dans le dossier ./benchmarks/loading_csv_methods")

if __name__ == "__main__":
    main() 