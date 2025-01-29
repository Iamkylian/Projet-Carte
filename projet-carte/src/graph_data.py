"""
Ce fichier contient les données des jeux de données utilisés pour les tests.
"""

GRAPH_DATA = [
    {
        "name": "Serres-sur-Arget",
        "nodes": "./../data/france/serres-sur-arget/osm_nodes.csv",
        "ways": "./../data/france/serres-sur-arget/osm_ways.csv",
        "points": {
            "start": "469819297",    # Saint-Pierre-de-Rivière
            "end": ["469819297","1792742726", "8490363670", "1205464576"]  # Las Prados, Grotte Bernard, Cabane Coumauzil - barguillere
        }
    },
    {
        "name": "Ariège",
        "nodes": "./../data/france/ariege/osm_nodes.csv",
        "ways": "./../data/france/ariege/osm_ways.csv",
        "points": {
            "start": "469819297", # Saint-Pierre-de-Rivière
            "end": ["469819297", "1792742726", "8490363670"] # Las Prados, Grotte Bernard
        }
    },
    # {
    #     "name": "Midi-Pyrénées",
    #     "nodes": "./../data/france/midipyr/osm_nodes.csv",
    #     "ways": "./../data/france/midipyr/osm_ways.csv",
    #     "points": {
    #         "start": "469819297",
    #         "end": ["1792742726", "8490363670"] # Las Prados, Grotte Bernard
    #     }
    # }
] 