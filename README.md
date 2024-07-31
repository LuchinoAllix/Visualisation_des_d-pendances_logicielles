# Visualisation des dépendances logicielles

## Menu

1. [Informations générales](#informations-générales)
2. [Exécution](#exécution)
	* 2.1 [Obtention des données](#1-obtention-des-données)
	* 2.2 [Visualisation des données](#2-visualisation-des-données) to do
	* 2.3 [Bon à savoir](#3-bon-à-savoir-)
3. [Explication du code](#explication-du-code)
	* 3.1 [fetch.py](#fetchpy-)
	* 3.2 [convert.py](#convertpy-) to do
	* 3.3 [viz.html](#vizhtml-) to do
	* 3.1 [Organisation des fichiers](#organisation-des-fichiers)
4. [Contexte](#contexte)

## Informations générales

Ce repository contient du code qui sert à visualiser l'évolution des dépendances logicielles (de projets javascript) au cours des versions. Le code fonctionne en deux grosses parties :
	
	1) L'obtention des données en python
	2) La visualisation des données en javascript 

Grossièrement, `fetch.py` prend l'url d'un repo git et génère des fichiers `.json` pour chaque version. Dans chaque fichier se trouve la liste des dépendance et quelques métriques. Ensuite `convert.py` va transformer les fichiers `.json` pour qu'ils puissent être représenté graphiquement avec [D3.js](https://d3js.org/what-is-d3). Finalement `index.html` va crée les visualisations à l'aide d'un serveur.

## Exécution

Le code ne fonctionne pas en une traite, il y a deux opérations à faire :

### 1) Obtention des données
Pour obtenir les données : exécuter `main.py` avec l'url du repo du projet javascript à analyser :

Sous windows :

```
python main.py https://github.com/processing/p5.js
```

Sous unix :

```
python3 main.py https://github.com/processing/p5.js
```
> Si vous voulez toutes les métriques vous pouvez laisser tel quel, mais cela peut prendre du temps ( [expliqué ici](#3-bon-à-savoir-) ). Sinon vous pouvez spécifié que vous ne les voulez pas en rajoutant un argument : False

Les fichiers pour la visualisation seront prêts, il suffit de passer à la deuxième étape.

to do mentionner les libraires à dl + mettre le fichier .exe

### 2) Visualisation des données

todo

### 3) Bon à savoir !

> **Attention :** L'exécution du code est longue ! 

L'exécution du code peut prendre une heure comme un jour en fonction des choix et de la machine utilisée.

La raison principale de la lenteur du programme vient du fait que pour chaque version il faut obtenir la liste de contributeurs, hors cela requiert beaucoup d'interaction avec l'api de GitHub (qui limite le nombre d'interaction par heure). Il a fallut donc installer un buffer pour ralentir l'obtention des données. Il faut compter une journée (to do à verifier) avec le buffer et un peu moins d'une heure sans.  


## Explication du code

Ce code sert à obtenir des informations sur des projets `.js` pour ensuite créer des visualisation sur ces dernières.

Pour choisir le projet à analyser il faut le spécifier à l'exécution, [expliqué ici](#exécution).

`main.py` fait appel à `fetch.py` et `convert.py`. 

### `fetch.py` :

Ce code clone le repo du projet et utilise `npm` pour télécharger toutes les dépendances pour chaque version du projet. Une fois téléchargées elles sont mises sous forme d'arbre de dépendances et analysées.

Pour chaque version on obtient un fichier `.json` de la forme :

```
{
    "version": "",
  	"name": "",
  	"problems": [""],
  	"dependencies": { ... }
    "release_date": "xxxx-xx-xx xx:xx:xx",
    "commit_count": x,
    "last_commit_date": x,
    "contributor_count": x,
    "contributors": [...],
    "dependencies_count": x,
    "js_file_count": x,
    "json_file_count": x
}
```

et où chaque dépendance est de la forme :

```
{
  "version": "",
  "resolved":  "",
  "overridden" : x,
  "commit_count": x,
  "contributor_count": x,
  "dependencies": [...]
}
```
### `convert.py` :

todo

### `viz.html` :

todo

### Organisation des fichiers

Trois dossier vont être créer (s'ils n'existent pas déjà) :
- `deps` qui contiendra toutes les données de chaque versions du projet sous la forme `nomProjet_version.json`
- `tmp` qui contiendra le projet à analyser (qui sera supprimé à la fin de l'exécution)
- `trees` qui contiendra toutes les représentation des arbres sous forme de fichier `tree_nomProjet_version.json` 

Exemple avec p5.js :

```
 └── cwd
	├── deps
	|	├── p5_0.json
	|	├── p5_0.1.json
	|	|   ...
	|	└──
	├── tmp (vide)
	└── trees
		├── tree_p5_0.json
		├── tree_p5_0.1.json
		|   ...
		└──
```

Mise à part cela il y a un fichier `analyse.py` qui permet d'obtenir des idées générales les arbres qui ont été généré. Ces données sont utiles pour améliorer la visualisation. Pour l'instant elles ne servent qu'à faire des changement manuels dans la visualisation. Elle ont été sauvegardées dans `p5 tree data graphs`.


## Contexte

Ce travail est fait pour un cours de l'université de Montréal : projet d'informatique (IFT 3150).