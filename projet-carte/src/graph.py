import math
import polars as pl

class Node:
    """Classe représentant un nœud dans le graphe.
    
    Cette classe stocke les informations d'un point géographique
    et ses connexions avec d'autres nœuds.
    
    Attributs:
        id (str): Identifiant unique du nœud
        lat (float): Latitude du point
        lon (float): Longitude du point 
        name (str): Nom du lieu
        neighbors (dict): Dictionnaire des voisins {id_noeud: distance}
    """
    def __init__(self, id, lat, lon, name):
        self.id = id
        self.lat = lon  # Inversion lat/lon pour correspondre au format OSM
        self.lon = lat
        self.name = name
        self.neighbors = {}  # Stockage des voisins avec leur distance

class Graph:
    """Classe représentant un graphe pour les calculs d'itinéraires.
    
    Cette classe permet de construire et manipuler un graphe à partir de données OSM
    pour calculer des distances et des plus courts chemins.
    
    Attributs:
        nodes (dict): Dictionnaire des nœuds avec leurs coordonnées {id: Node}
    """
    
    def __init__(self):
        """Initialise un nouveau graphe vide."""
        self.nodes = {}  # {id: Node}
        
    def add_node(self, id, lat, lon, name):
        self.nodes[id] = Node(id, lat, lon, name)
    
    def add_edge(self, id1, id2, distance):
        if id1 in self.nodes and id2 in self.nodes:
            self.nodes[id1].neighbors[id2] = distance
            self.nodes[id2].neighbors[id1] = distance  # Pour les routes bidirectionnelles

    def load_from_csv(self, nodes_file, ways_file):
        """ Charge le graphe à partir des fichiers CSV.
        
        Args:
            nodes_file (str): Chemin vers le fichier des nœuds
            ways_file (str): Chemin vers le fichier des routes
        """
        
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

    def dijkstra(self, start_id, end_id):
        """Trouve le plus court chemin entre deux points avec l'algorithme de Dijkstra.
        
        Args:
            start_id (str): Identifiant du nœud de départ
            end_id (str): Identifiant du nœud d'arrivée
            
        Returns:
            tuple: (distance totale, liste des identifiants des nœuds du chemin)
        """
        from heapq import heappush, heappop
        
        distances = {start_id: 0}
        predecessors = {start_id: None}
        pq = [(0, start_id)]
        
        while pq:
            dist, current = heappop(pq)
            
            if current == end_id:
                path = []
                while current:
                    path.append(current)
                    current = predecessors[current]
                return dist, path[::-1]
            
            if current in distances and dist > distances[current]:
                continue
            
            # Accès direct aux voisins O(1) au lieu de O(E)
            for neighbor, edge_dist in self.nodes[current].neighbors.items():
                new_dist = dist + edge_dist
                
                if neighbor not in distances or new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current
                    heappush(pq, (new_dist, neighbor))
        
        return float('inf'), []

    def print_path(self, path, total_distance):
        """ Affiche le chemin trouvé avec les détails des nœuds.
        
        Args:
            path (list): Liste des identifiants des nœuds du chemin
            total_distance (float): Distance totale du chemin
        """
        for i, node_id in enumerate(path):
            node = self.nodes[node_id]
            if i == 0:
                print(f"{i} - From: ['{node_id}', '{node.name or 'None'}', '{node.lat}', '{node.lon}']")
            else:
                print(f"{i} - To: ['{node_id}', '{node.name or 'None'}', '{node.lat}', '{node.lon}']: distance = {total_distance if i == len(path)-1 else 0} km")

    def haversine_distance(self, id1, id2):
        """Calcule la distance de Haversine entre deux points.
        
        La formule de Haversine permet de calculer la distance à vol d'oiseau
        entre deux points sur une sphère.
        
        Args:
            id1 (str): Identifiant du premier point
            id2 (str): Identifiant du second point
            
        Returns:
            float: Distance en kilomètres entre les deux points
        """
        node1 = self.nodes[id1]
        node2 = self.nodes[id2]
        
        # Correction de l'inversion lat/lon
        lat1, lon1 = math.radians(node1.lat), math.radians(node1.lon)
        lat2, lon2 = math.radians(node2.lat), math.radians(node2.lon)
        
        # Rayon de la Terre en km
        R = 6371.0
        
        # Formule de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def a_star(self, start_id, end_id):
        """Trouve le plus court chemin entre deux points avec l'algorithme A*.
        
        Utilise une heuristique (distance de Haversine) pour optimiser la recherche
        par rapport à l'algorithme de Dijkstra.
        
        Args:
            start_id (str): Identifiant du nœud de départ
            end_id (str): Identifiant du nœud d'arrivée
            
        Returns:
            tuple: (distance totale, liste des identifiants des nœuds du chemin)
        """
        from heapq import heappush, heappop
        import math
        
        # Initialisation
        g_score = {start_id: 0}  # Real cost from start
        f_score = {start_id: self.haversine_distance(start_id, end_id)}  # Estimated total cost
        came_from = {start_id: None}
        open_set = [(f_score[start_id], start_id)]  # (f_score, node_id)
        
        while open_set:
            current_f, current = heappop(open_set)
            
            if current == end_id:
                # Path reconstruction
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return g_score[end_id], path[::-1]
            
            # Explore neighbors
            for neighbor, edge_dist in self.nodes[current].neighbors.items():
                tentative_g = g_score[current] + edge_dist
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.haversine_distance(neighbor, end_id)
                    heappush(open_set, (f_score[neighbor], neighbor))
        
        return float('inf'), []  # No path found