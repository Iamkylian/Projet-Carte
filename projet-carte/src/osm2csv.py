import argparse
from osmread import parse_file, Way, Node
import itertools
from geopy import distance
import os

def main():
    # Configuration des arguments avec argparse
    parser = argparse.ArgumentParser(description="Traitement des données OSM pour extraire les nœuds et les chemins dans un format intermédiaire.")
    parser.add_argument("pbf_file", type=str, help="Chemin vers le fichier OSM source .pbf.")
    parser.add_argument("output_dir", type=str, help="Dossier où seront enregistrés les fichiers CSV de sortie.")
    args = parser.parse_args()

    # Création du dossier de sortie s'il n'existe pas
    os.makedirs(args.output_dir, exist_ok=True)

    # Chemins pour les fichiers de sortie
    output_nodes_path = os.path.join(args.output_dir, "osm_nodes.csv")
    output_ways_path = os.path.join(args.output_dir, "osm_ways.csv")

    nodes = {}
    ways = {}

    # Lecture du fichier PBF
    for entity in parse_file(args.pbf_file):
        if isinstance(entity, Way) and 'highway' in entity.tags:
            ways[entity.id] = entity
        if isinstance(entity, Node):
            nodes[entity.id] = entity

    # Écriture des nœuds dans le fichier CSV
    with open(output_nodes_path, "w") as output_nodes:
        output_nodes.write("id,name,lon,lat,highway\n")  # En-têtes
        for id, entity in nodes.items():
            name = entity.tags.get("name", "")
            highway = entity.tags.get("highway", "")
            output_nodes.write(f"{entity.id},{name},{entity.lon},{entity.lat},{highway}\n")

    # Écriture des chemins dans le fichier CSV
    with open(output_ways_path, "w") as output_ways:
        output_ways.write("name,ref,node_from,node_to,highway,destination,distance_km\n")  # En-têtes
        for id, entity in ways.items():
            name = entity.tags.get("name", "")
            ref = entity.tags.get("ref", "")
            destination = entity.tags.get("destination", "")
            combinations = list(itertools.combinations(entity.nodes, 2))
            for c in combinations:
                if c[0] in nodes and c[1] in nodes:
                    c_from = (nodes[c[0]].lat, nodes[c[0]].lon)
                    c_to = (nodes[c[1]].lat, nodes[c[1]].lon)
                    dist = distance.distance(c_from, c_to).km
                    output_ways.write(f'"{name}","{ref}",{c[0]},{c[1]},"{entity.tags.get("highway", "")}","{destination}",{dist}\n')

    print(f"Les fichiers CSV ont été créés dans le dossier : {args.output_dir}")

if __name__ == "__main__":
    main()
