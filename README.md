# Compte Rendu - Projet Carte

| Version | Date | Auteur | Module |
|---------|------|--------|--------|
| 1.0 | 22 janvier 2025 | Kylian GACHET 2B | R5.A.04 - Qualité algorithmique |

## Sommaire
- [Compte Rendu - Projet Carte](#compte-rendu---projet-carte)
  - [Sommaire](#sommaire)
  - [1. Description du projet](#1-description-du-projet)
  - [2. Algorithme de Dijkstra (1956)](#2-algorithme-de-dijkstra-1956)
    - [2.1 Présentation de l'algorithme](#21-présentation-de-lalgorithme)
    - [2.2 Problèmes identifiés](#22-problèmes-identifiés)
    - [2.3 Solutions proposées](#23-solutions-proposées)
  - [3. Algorithme A\* (1968)](#3-algorithme-a-1968)
    - [3.1 Présentation de l'algorithme](#31-présentation-de-lalgorithme)
    - [3.2 Problèmes identifiés](#32-problèmes-identifiés)
    - [3.3 Solutions proposées](#33-solutions-proposées)
  - [4. Benchmark et Analyse](#4-benchmark-et-analyse)
    - [4.1 Complexités théoriques](#41-complexités-théoriques)
    - [4.2 Mesures de performance](#42-mesures-de-performance)
  - [5. Perspectives d'amélioration](#5-perspectives-damélioration)
  - [6. Conclusion](#6-conclusion)

## 1. Description du projet

Le projet consiste à développer et optimiser un système de calcul d'itinéraire basé sur des données OpenStreetMap. L'objectif est d'implémenter et de comparer différents algorithmes de recherche de chemin pour trouver le trajet optimal entre deux points sur une carte.

## 2. Algorithme de Dijkstra (1956)

### 2.1 Présentation de l'algorithme
Développé par Edsger Dijkstra, cet algorithme trouve le plus court chemin entre deux points dans un graphe pondéré. 

**Principes clés :**
- Exploration progressive des nœuds à partir du point de départ
- Maintient une liste des distances minimales connues
- Visite systématiquement le nœud non visité le plus proche
- Garantit de trouver le chemin optimal

**Applications :**
- Routage réseau
- Navigation GPS
- Planification d'itinéraires

### 2.2 Problèmes identifiés
- Temps d'exécution élevé (11.64s pour un trajet court de ~0.43km)
- Exploration excessive de nœuds non pertinents
- Recherche linéaire dans les edges pour trouver les voisins
- Stockage redondant des arêtes bidirectionnelles

### 2.3 Solutions proposées
- Restructurer le graphe pour un accès O(1) aux voisins
- Utiliser des sets pour les nœuds visités
- Orienter la recherche vers la destination pour éviter l'exploration inutile de nœuds
- Utiliser une estimation de la distance restante pour prioriser les nœuds prometteurs
- Réduction du graphe aux nœuds essentiels

> _Note : Les deux solutions concernant l'orientation de la recherche et l'estimation de la distance sont précisément ce que propose l'algorithme A*, qui sera présenté dans la section suivante._

## 3. Algorithme A* (1968)

### 3.1 Présentation de l'algorithme
Développé par Peter Hart, Nils Nilsson et Bertram Raphael, A* est une extension de l'algorithme de Dijkstra qui utilise une heuristique pour accélérer la recherche.

**Principes clés :**
- Combine le coût réel (comme Dijkstra) avec une estimation heuristique


> _Qu'est ce qu'une heuristique ?_
> 
>> Une heuristique est une estimation de la distance restante pour atteindre la destination. Elle est utilisée pour accélérer la recherche.
>> Dans le contexte de A*, l'heuristique (comme la distance à vol d'oiseau) permet d'orienter la recherche vers la destination en estimant la distance restante, même si cette estimation n'est pas exacte, elle doit être optimiste (ne jamais surestimer la distance réelle).

- Utilise une fonction f(n) = g(n) + h(n)
  - g(n) : coût réel depuis le départ
  - h(n) : estimation heuristique jusqu'à l'arrivée
- Guide la recherche vers la destination

**Différences clés avec Dijkstra :**
1. **Direction de recherche :**
   - Dijkstra explore uniformément dans toutes les directions
   - A* oriente sa recherche vers la destination grâce à l'heuristique
2. **Efficacité :**
   - A* explore moins de nœuds grâce à l'heuristique
   - Plus rapide quand l'heuristique est bien choisie
3. **Optimalité :**
   - Les deux garantissent le chemin optimal
   - A* nécessite une heuristique admissible (qui ne surestime jamais)

### 3.2 Problèmes identifiés
- Heuristique potentiellement sous-optimale
- Utilisation intensive de la mémoire
- Pas d'optimisation pour les grands graphes
- Absence de pré-traitement des données

### 3.3 Solutions proposées
- Amélioration de l'heuristique
- Implémentation de la recherche bidirectionnelle
- Pré-calcul des chemins fréquents
- Mise en cache des résultats

## 4. Benchmark et Analyse

### 4.1 Complexités théoriques

| Algorithme | Temporelle | Spatiale |
|------------|------------|----------|
| Dijkstra   | O(V² + E)  | O(V)     |
| A*         | O(E)       | O(V)     |

### 4.2 Mesures de performance

Tests réalisés sur différents jeux de données :
1. Serres sur Arget (petit)
2. Ariège (moyen)
3. Occitanie (large)

```
Résultats pour un trajet de 0.43 km :
- Dijkstra : 11.646 secondes
- A* : 5.823 secondes [à mesurer]
```

[Ajouter graphiques de performance]

## 5. Perspectives d'amélioration

1. **Court terme :**
   - Implémentation de Contraction Hierarchies
   - Optimisation des structures de données
   - Amélioration de l'heuristique A*

2. **Long terme :**
   - Support multi-threading
   - Système de cache intelligent
   - API de calcul d'itinéraire

## 6. Conclusion

Le projet a permis d'implémenter et de comparer différentes approches de calcul d'itinéraire. Les optimisations proposées devraient permettre d'améliorer significativement les performances, particulièrement pour les grands jeux de données. L'implémentation de Contraction Hierarchies représente la prochaine étape majeure d'amélioration.




Benchmark : temps d'execution, memoire utilisé (spatiale)
