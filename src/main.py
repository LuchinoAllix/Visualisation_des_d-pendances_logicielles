import os
import subprocess
import json
import requests
import re
import shutil
import stat
from git import Repo


def deleteDir(dossier):
    # Fonction pour changer les permissions de tous les fichiers dans le dossier
    for root, dirs, files in os.walk(dossier):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)
    
    # Supprime le dossier et tout son contenu
    shutil.rmtree(dossier)

# fonction récursive pour obtenir toutes les dépendances
def extract_dependencies(deps, result):
	if deps is None:
		return
	for dep, details in deps.items():
		if dep not in result:
			result.add(dep)
			extract_dependencies(details.get('dependencies'), result)

def commitCount(u, r):
	# https://gist.github.com/codsane/25f0fd100b565b3fce03d4bbd7e7bf33
	response = requests.get(f'https://api.github.com/repos/{u}/{r}/commits?per_page=1')
	last_page_url = response.links['last']['url']
	return re.search(r'\d+$', last_page_url).group()

def contributorsCount(u, r):
	# https://gist.github.com/codsane/25f0fd100b565b3fce03d4bbd7e7bf33
	response = requests.get(f'https://api.github.com/repos/{u}/{r}/contributors?per_page=1')
	last_page_url = response.links['last']['url']
	return re.search(r'\d+$', last_page_url).group()

def get_data(repo_url):
	# Extraire le nom du propriétaire et le nom du repo à partir de l'URL
	# Exemple d'URL : https://github.com/processing/p5.js
	parts = repo_url.strip('/').split('/')
	owner = parts[-2]
	repo_name = parts[-1]

	# URLs de l'API GitHub pour les commits et les contributeurs
	commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"

	try:
		# Faire une requête GET à l'API GitHub pour les commits
		response_commits = requests.get(commits_url)
		response_commits.raise_for_status()  # Lève une exception pour les erreurs HTTP

		last_commit_date = response_commits.json()[0]['commit']['author']['date']
		contributors_count = contributorsCount(owner,repo_name)
		commits_count = commitCount(owner,repo_name)

		return commits_count, last_commit_date, contributors_count

	except requests.exceptions.RequestException as e:
		print(f"Erreur lors de la récupération des données pour {repo_url}: {e}")
		return None, None, None

def count_files(repo_path):
	js_files = 0
	json_files = 0

	for root, dirs, files in os.walk(repo_path):
		for file in files:
			if file.endswith('.js'):
				js_files += 1
			elif file.endswith('.json'):
				json_files += 1

	return js_files, json_files

# Liste des projets à analyser
projects_url = ["https://github.com/processing/p5.js"
			,"https://github.com/Tonejs/Tone.js"
			,"https://github.com/meezwhite/p5.grain"]

#projects_url = ["https://github.com/meezwhite/p5.grain"]

# path de ce fichier
current_dir = os.path.dirname(os.path.abspath(__file__))
git_error = 0

# vérifie que les dir tmp et deps existent sinon les crées
tmp = os.path.join(current_dir,'tmp')
if not os.path.exists(tmp):
	os.makedirs(tmp)

deps = os.path.join(current_dir,'deps')
if not os.path.exists(deps):
	os.makedirs(deps)

for repo_url in projects_url :

	repo_name = repo_url.split('/')[-1].replace('.git', '')
	repo_path = os.path.join(tmp,repo_name)

	print(f'Analyse de {repo_name}')

	# on supprime le dossier si déjà présent
	if os.path.exists(repo_path):
		deleteDir(repo_path)

	try :
		print(f'clonnage de {repo_name}')
		repo = Repo.clone_from(repo_url, repo_path)
		print(f'repo {repo_name} clonné avec succés')
	except Exception as e:
		print(f'Erreur lors du clonage du répo {repo_name} : {e}')
		exit(1)

	# on vide le dossier deps
	depsRepo = os.path.join(deps,repo_name)
	if os.path.exists(depsRepo) :
		deleteDir(depsRepo)

	tags = [tag.name for tag in repo.tags]

	for tag in tags :

		try :
			repo.git.checkout(tag)		

			versionFolder = os.path.join(deps,repo_name,tag)

			if not os.path.exists(versionFolder):
				os.makedirs(versionFolder)

			depsfile = os.path.join(versionFolder,repo_name + 'v' + tag +'.json')

			try:
				# npm ci (installe toutes les dépendances)
				subprocess.run(['npm', 'ci'],capture_output=True,shell=True, cwd=repo_path)
			except subprocess.CalledProcessError as e:
				print(f'Erreur lors de l\'exécution de npm ci : {e}')

			try:
				# npm list -all -json > alldeps.json (création du fichier avec toutes les dépendances)
				subprocess.run(['npm', 'list','-all','-json', '>',depsfile],capture_output=True,shell=True, cwd=repo_path)

				# rm -rf node_modules (supprime toutes les dépendances)
				subprocess.run(['rm', '-rf','node_modules'], capture_output=True, shell=True, cwd=repo_path)
			except subprocess.CalledProcessError as e:
				print(f'Erreur lors de la création de depsfile : {e}')
				
			with open(depsfile, 'r') as file:
				data = json.load(file)

			all_dependencies = set()
			extract_dependencies(data.get('dependencies'), all_dependencies)

			# api_data = get_data(repo_url)
			# pour éviter de spam l'api github
			api_data=[0,0,0]
			files_data = count_files(repo_path)
			
			print(f'\nDonnées de {repo_name} version : {tag}:')

			print(f'nombre de dépendances :{len(all_dependencies)}')
			print(f'nombre de commits : {api_data[0]}')
			print(f'date dernier commit : {api_data[1]}')
			print(f'nombre de contributeurs : {api_data[2]}')
			print(f'nombre de fichier .js : {files_data[0]}')
			print(f'nombre de fichier .json : {files_data[1]}')

			print('\n')
		
		except :
			git_error+=1

	deleteDir(repo_path)

print(git_error)
