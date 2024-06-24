import os
import subprocess
import json
from git import Repo

# Liste des projets à analyser
projects_url = ["https://github.com/processing/p5.js"
			,"https://github.com/Tonejs/Tone.js"
			,"https://github.com/meezwhite/p5.grain"]

# path de ce fichier
current_dir = os.path.dirname(os.path.abspath(__file__))

# vérifie que les dir tmp et deps existent sinon les crées
tmp = os.path.join(current_dir,'tmp')
if not os.path.exists(tmp):
	os.makedirs(tmp)

deps = os.path.join(current_dir,'deps')
if not os.path.exists(deps):
	os.makedirs(deps)

# fonction récursive pour obtenir toutes les dépendances
def extract_dependencies(deps, result):
    if deps is None:
        return
    for dep, details in deps.items():
        if dep not in result:
            result.add(dep)
            extract_dependencies(details.get('dependencies'), result)

for repo_url in projects_url :

	repo_name = repo_url.split('/')[-1].replace('.git', '')
	repo_path = os.path.join(tmp,repo_name)

	print(f'Analyse de {repo_name}')

	# on clone que si on n'a pas déjà le projet
	if not os.path.exists(repo_path):
		try :
			print(f'clonnage de {repo_name}')
			Repo.clone_from(repo_url, repo_path)
			print(f'repo {repo_name} clonné avec succés')
		except :
			print(f'Erreur lors du clonage du répo {repo_name} : {e}')
	else :
		print(f'Pas de clonnage de {repo_name} car déjà présent')

	depsfile = os.path.join(deps,repo_name + '.json')

	# on se déplace dans le dir du répo pour exxécuter les commandes bash
	os.chdir(repo_path) 

	# npm ci
	try:
		print('run npm ci')
		subprocess.run(['npm', 'ci'],capture_output=True,shell=True)
		print('npm ci exécuté avec succès.')
	except subprocess.CalledProcessError as e:
		print(f'Erreur lors de l\'exécution de npm ci : {e}')

	# npm list -all -json > alldeps.json
	try:
		print('run npm list -all -json > alldeps.json')
		subprocess.run(['npm', 'list','-all','-json', '>',depsfile],capture_output=True,shell=True)
		print('depsfile crée avec succès.')
	except subprocess.CalledProcessError as e:
		print(f'Erreur lors de la création de depsfile : {e}')
		

	with open(depsfile, 'r') as file:
		data = json.load(file)

	all_dependencies = set()
	extract_dependencies(data.get('dependencies'), all_dependencies)

	print(f'nombre de dépendances :{len(all_dependencies)}')

	print('\n')