import math
import polars as pl

class Node:
    def __init__(self, id, lat, lon, name):
        self.id = id
        self.lat = lon
        self.lon = lat
        self.name = name
        self.neighbors = {}  # {node_id: distance}

class Graph:
    """Class representing a graph for path calculations.
    
    This class allows building and manipulating a graph from OSM data
    to calculate distances and shortest paths.
    
    Attributes:
        nodes (dict): Dictionary of nodes with their coordinates {id: Node}
    """
    
    def __init__(self):
        """Initialize a new empty graph."""
        self.nodes = {}  # {id: Node}
        
    def add_node(self, id, lat, lon, name):
        self.nodes[id] = Node(id, lat, lon, name)
    
    def add_edge(self, id1, id2, distance):
        if id1 in self.nodes and id2 in self.nodes:
            self.nodes[id1].neighbors[id2] = distance
            self.nodes[id2].neighbors[id1] = distance  # Pour les routes bidirectionnelles

    def load_from_csv(self, nodes_file, ways_file):
        """Load the graph from CSV files using Polars.
        
        Args:
            nodes_file (str): Path to the nodes CSV file
            ways_file (str): Path to the ways CSV file
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
        """Find the shortest path between two points using Dijkstra's algorithm.
        
        Args:
            start_id (str): ID of the starting node
            end_id (str): ID of the destination node
            
        Returns:
            tuple: (total distance, list of node IDs in the path)
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
        """ Print the path found with the details of the nodes.
        
        Args:
            path (list): List of node IDs in the path
            total_distance (float): Total distance of the path
        """
        for i, node_id in enumerate(path):
            node = self.nodes[node_id]
            if i == 0:
                print(f"{i} - From: ['{node_id}', '{node.name or 'None'}', '{node.lat}', '{node.lon}']")
            else:
                print(f"{i} - To: ['{node_id}', '{node.name or 'None'}', '{node.lat}', '{node.lon}']: distance = {total_distance if i == len(path)-1 else 0} km")

    def haversine_distance(self, id1, id2):
        """Calculate the haversine distance between two points.
        
        Args:
            id1 (str): ID of the first point
            id2 (str): ID of the second point
            
        Returns:
            float: The haversine distance between the two points
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
        """Find the shortest path between two points using A* with haversine distance.
        
        Args:
            start_id (str): ID of the starting node
            end_id (str): ID of the destination node
            
        Returns:
            tuple: (total distance, list of node IDs in the path)
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