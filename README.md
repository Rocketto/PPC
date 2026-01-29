# PROJET PPC

## Introduction

Ce projet met en oeuvre une simulation reposant sur le module `multiprocessing` de Python, avec une visualisation en temps réel des données à l’aide de la bibliothèque `matplotlib`.

## Mise en place de l’environnement

Le projet nécessite l’utilisation de bibliothèques Python externes, notamment matplotlib. Il est donc indispensable de préparer un environnement Python isolé avant l’exécution du programme.

La méthode recommandée consiste à créer un environnement virtuel Python dans le répertoire contenant les fichiers sources.

### Création de l’environnement virtuel

```shell
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### Réutilisation de l’environnement

À chaque nouvelle session, l’environnement virtuel peut être réactivé avec la commande suivante :

```shell
source .venv/bin/activate
```

## Utilisation du programme 

Une fois l'environnement virtuel activé , executer la commande suivante:

```shell
python3 environment.py
```

Ce programme lance plusieurs processus distincts :

- le processus principal environment, chargé d’initialiser l’environnement, de créer et démarrer l’ensemble des autres processus, ainsi que de gérer la croissance de l’herbe ;

- le processus display, qui s’appuie sur la bibliothèque matplotlib pour afficher en temps réel l’évolution des différentes populations ;

- les processus représentant les animaux, à savoir les proies et les prédateurs, exécutés de manière concurrente.


## Paramètres de démarrage

Les paramètres d’initialisation des différents processus sont définis dans la structure parameters, située dans le fichier environment.py.
Cette structure permet de configurer l’état initial de l’environnement ainsi que les caractéristiques des différentes entités simulées.

## Utilisation de l'interface graphique

L’interface graphique permet de visualiser l’évolution des populations en fonction du temps sous forme de courbes.
La valeur instantanée de chaque population est également affichée.

L’utilisateur peut interagir avec la simulation à l’aide de boutons permettant de :

- déclencher une période de sécheresse d’une durée de cinq unités de temps ;

- ajouter une proie à l’environnement ;

- ajouter un prédateur à l’environnement.
