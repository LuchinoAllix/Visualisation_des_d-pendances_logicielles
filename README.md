# Visualisation des dépendances logicielles

## Menu

1. [Informations générales](#informations-générales)
2. [Exécution](#exécution)
	* 2.1 [Obtention des données](#1-obtention-des-données)
	* 2.2 [Visualisation des données](#2-visualisation-des-données)
3. [Explication du code](#explication-du-code)
	* 3.1 [fetch.py](#fetchpy-)
	* 3.2 [convert.py](#convertpy-)
	* 3.3 [Treeviz.html](#treevizhtml-)
	* 3.4 [Script.js](#scriptjs-)
	* 3.5 [Organisation des fichiers](#organisation-des-fichiers)
4. [Contexte](#contexte)
5. [Known Issues](#known-issues)
6. [Improvement](#improvements)

## Informations générales

Ce repository contient du code qui sert à visualiser l'évolution des dépendances logicielles (de projets javascript) au cours des versions. Le code fonctionne en deux grosses parties :
	
1) L'obtention des données en python  
2) La visualisation des données en javascript 

Grossièrement, `fetch.py` prend l'url d'un repo git et génère des fichiers `.json` pour chaque version. Dans chaque fichier se trouve la liste des dépendance et quelques métriques. Ensuite `convert.py` va transformer les fichiers `.json` pour qu'ils puissent être représenté graphiquement avec [D3.js](https://d3js.org/what-is-d3). Finalement, `TreeViz.html` va crée les visualisations à l'aide `Script.js`.

Exemple des résultats : [ici](https://www-ens.iro.umontreal.ca/ete/~allixlal/3150/VDL/TreeViz.html)

## Exécution

Le code ne fonctionne pas en une traite, il y a deux opérations à faire :

### 1) Obtention des données
-> En premier lieu il faut remplir le fichier `token.txt` avec un token d'authentification GitHub. Vu que ce code fait un grand nombre de requêtes à l'api GitHub (pour [P5.js](https://github.com/processing/p5.js) ~ 6000 requêtes) il faut utiliser un token, qui permet 5000 ~ requêtes par heure contre 60 en temps normal ([source](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28)). Ce facteur de 80 est non négligeable.

>  L'exécution du code est longue, pour une librairie comme [P5.js](https://github.com/processing/p5.js) cela peut prendre du temps, jusqu'à 1h30 ! 

-> En deuxième lieu il faut installer certaines librairies python :

```
pip install requests matplotlib gitpython
```

-> Le code utilise [`npm`](https://www.npmjs.com/), il faut que ce soit installé.

-> Finalement, pour obtenir les données : exécuter `main.py` avec l'url du repo du projet javascript à analyser (ou rien, par déault le repo analysé est [P5.js](https://github.com/processing/p5.js)):

Sous windows :

```
python main.py https://github.com/processing/p5.js
```

Sous unix :

```
python3 main.py https://github.com/processing/p5.js
```

> Attention, ce code a été développé sous windows, il fonctionne sous unix mais il y a quelques problèmes, notament avec la génération des couleurs des arbres, [voir plus](#known-issues).

Les fichiers pour la visualisation seront prêts, il suffit de passer à la deuxième étape.


### 2) Visualisation des données

Pour visualiser le resultat, il faut mettre en place une façon de visionner une page web qui interagit avec un script `.js` Pour ce faire, soit uploader le dossier `Visualisation` sur un server (mettre tous les fichier en droit admin 0755) ou bien utiliser une extension vs code comme [celle-ci](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) sur le fichier `TreeViz.html`. Il y a bien d'autres options, celles-ci ne sont que des exemples.

Différentes visualisation sont générée :
- Une coloration des arbres qui au fur des versions indique quelles dépendances sont nouvelles
- Une coloration des arbres qui indique le nombre de contributeur par dépendance
- Une coloration des arbres qui indique le nombre de commits par dépendance

Il y a aussi une façon de trier les arbres, selon la date de publication de la version ou par ordre alphabétique des version, car ce ne sont pas toujours les mêmes.

## Explication du code

Ce code sert à obtenir des informations sur des projets `.js` pour ensuite créer des visualisation sur ces dernières.

Pour choisir le projet à analyser il faut le spécifier à l'exécution, [expliqué ici](#exécution).

`main.py` fait appel à `fetch.py`, `convert.py` et `normalize.py`. 

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
  "contributors": [...]
  "dependencies": [...]
}
```

Un fichier `version-date.json` est aussi crée, il contient un dictionnnaire qui associe chaque version à sa date de publication, pour pourvoir trier les fichiers sans avoir à aller chercher des informations à l'interieur. 

### `convert.py` :

Convert crée 6 dossiers, chacun avec des fichiers `.json` qui représentent des arbres de la forme :

```
{
  "name": "p5.grain",
  "value": 10,
  "type": "rgba(12,7,134,1.0)",
  "level": "rgba(12,7,134,1.0)",
  "children": [...],
  "version": "0.2.0",
  "date": "2022-09-14 22:48:32",
  "dir": "v0.2.0",
  "maxCommit": 3372,
  "maxContributors": 226,
  "nbVersion": 8
}
```

Ces arbres peuvent êtres lu par le script `.js` pour être visualisé avec [D3.js](https://d3js.org/what-is-d3).

Pour chaque visualisation, une échelle de couleur est basée sur le nombre de cas différent (le nombre de version, commit ou contributeur). Chaque visualisation doit pourvoir être triée différemment, donc l'échelle est appliqué d'abord selon un ordre, l'arbres est enregistré, puis elle est appliqué selon un autre ordre. Des fichier css avec l'échelle de coloration sont crées également.

Pour que le script puisse lire les fichiers, ils sont listés dans des fichiers de référence. Par exemple, pour les arbres coloré avec selon la version et trié par date, le fichier de référence sera : `path_verions_d`. Les menu de selection du script permettent de séléctionner correctement quel fichier de référence est requis.

### `TreeViz.html` :

La visualisation est relativement simple, une page avec des menu de selection et un slider pour naviguer à travers les arbres généres. On peut choisir quel donnée ont veut visualiser et selon quel ordre les arbres doivent être triées.

### `Script.js` :

Ce code permet de crée les arbres et de les injecter dans la page web `TreeViz.html`, pour cela elle récupère les informations ddes menus de selection et du slider pour savoir quel arbre générer.

### Organisation des fichiers

Trois dossiers vont être créer (s'ils n'existent pas déjà) :
- `deps` qui contiendra toutes les données de chaque versions du projet sous la forme `nomProjet_version.json`
- `tmp` qui contiendra le projet à analyser (qui sera supprimé à la fin de l'exécution)
- `Visualisation` qui contiendra toutes les représentation des arbres sous forme de fichier `.json` et les éléments pour les affichier (page `html`,`js` et `css`) 

Exemple avec p5.js :

```
└── cwd (src)
    ├── deps
    |   ├── p5_0.0.json
    |   ├── p5.0.1.json
    |   |   ...
    |   └── version-date.json
    ├── tmp (vide)
    └── Visualisation
        ├── Trees
        |   ├── commit_d
        |   |   ├── XXXX-XX-XX XX-XX-XX.json
        |   |   ├── XXXX-XX-XX XX-XX-XX.json
        |   |   ...
        |   |   └──
        |   ├── commit_v
        |   |   ├── 0.0.json
        |   |   ├── 0.1.json
        |   |   ...
        |   |   └──
        |   ...
        |   ├── colors_commit.css
        |   ├── colors_contributors.css
        |   ├── colors_versions.css
        |   ├── paths_commit_d.json
        |   ├── paths_commit_v.json
        |   ...
        |   └── paths_version_v
        ├── script.js
        ├── style.css
        └── TreeViz.html

```

Mise à part cela il y a un fichier `analyse.py` qui permet d'obtenir des idées générales les arbres qui ont été généré. Ces données sont utiles pour améliorer la visualisation. Pour l'instant elles ne servent qu'à faire des changement manuels dans la visualisation. Elle ont été sauvegardées dans `p5 tree data graphs`.


## Contexte

Ce travail est fait pour un cours de l'université de Montréal : [projet d'informatique (IFT 3150)](https://www-ens.iro.umontreal.ca/ete/~allixlal/3150/index.html).

## Known Issues

to do

## Improvements

to do