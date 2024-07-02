# Visualisation des dépendances logicielles

## Éxécution
Pour run le code : éxécuter `main.py`

Deux dossier vont être créer (s'il n'existent pas déjà)
- `tmp` qui contiendra les projets à analyser (qui seront supprimé)
- `deps` qui contiendra un sous dossier par projet, chaque projet possédera des sous dossier pour chaque version. Chaque version possèdera deux fichiers `.json ` :
	- les dépendances de chaque projet `projet.js_v_deps.json`
	- les informations de chaque projet `projet.js_v_data.json`

Exemple avec p5.js :

```
 └── src
	├── deps
		└── p5.js
			├── 0
				├── p5.js_0_data.json
				└── p5.js_0_deps.json
			├── 0.1
				├── p5.js_0.1_data.json
				└── p5.js_0.1_deps.json
			 .
			 .
			 .

			└──
	└── tmp (vide)
```

## Explication du code

Ce code sert à obtenir des informations sur des projets `.js` pour ensuite créer des visualisation sur ces dernières (pas encore implémentée).

Pour choisir les projets à analyser il faut les spécifier dans `projects_url` dans le fichier `main.py`.

Ce code clone le repo du projet et utilise `npm` pour télécharger toutes les dépendances pour chaque version du projet dans `projet.js_v_deps.json`. Ces dépendances sont sous la forme :
```
{
  "version": "",
  "name": "",
  "problems": [""],
  "dependencies": { ... }
}
```

où chaque dépendance à ses propres dépendances indiquées.

Également, avec l'api de GitHub, certaines données sont téléchargée dans `projet.js_v_data.json`. Elles sont de la forme :

```
data_json = {
	"repo_name": _ ,
	"release_date": _ ,
	"version": _ ,
	"dependencies_file_path": _ ,
	"commit_count": _ ,
	"last_commit_date": _ ,
	"contributor_count": _ ,
	"contributors": [_] ,
	"dependencies" : _ ,
	"js_file_count": _ ,
	"json_file_count": _
}
```
