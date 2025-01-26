
# Base de travail OSM

  
## Préparation des données

### Télécharger un PBF
https://download.openstreetmap.fr/extracts/europe/
### Extraire une zone depuis un fichier PBF
```
apt install -y osmium-tools
osmium extract -o serres-saintpierre-de-riviere.pbf ariege.osm.pbf -b '1.489942,42.935747,1.572511,43.000311'
```

Note: pour récupérer la bouding box: https://boundingbox.klokantech.com/, format CSV RAW
### Convertir un PBF en CSV

Installer osmread (https://github.com/dezhin/osmread)

```
# python3 osm2csv.py -h
usage: osm2csv.py [-h] pbf_file output_dir

Traitement des données OSM pour extraire les nœuds et les chemins dans un format intermédiaire.

positional arguments:
  pbf_file    Chemin vers le fichier OSM source .pbf.
  output_dir  Dossier où seront enregistrés les fichiers CSV de sortie.
```

Ce script génère deux fichiers:

- osm_nodes.csv: Points de la cartes.
- osw_ways.csv: chemins avec distance (à vol d'oiseau). Utile pour construire le graphe

## Recherche d'une distance

TODO

## Recherche d'un chemin

TODO