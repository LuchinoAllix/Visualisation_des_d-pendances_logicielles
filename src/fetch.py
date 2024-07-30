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

def count_dependencies(data):
	all_dependencies = set()
	extract_dependencies(data.get('dependencies'), all_dependencies)
	return len(all_dependencies)

def commitCount(u, r):
	# https://gist.github.com/codsane/25f0fd100b565b3fce03d4bbd7e7bf33
	response = requests.get(f'https://api.github.com/repos/{u}/{r}/commits?per_page=1')
	last_page_url = response.links['last']['url']
	return re.search(r'\d+$', last_page_url).group()

def contributorsList(u, r):
    contributors = []
    page = 1
    while True:
        response = requests.get(f'https://api.github.com/repos/{u}/{r}/contributors', params={'page': page})
        data = response.json()
        if not data:
            break
        contributors.extend([contributor['login'] for contributor in data])
        page += 1
    return contributors

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
		contributors = contributorsList(owner,repo_name)
		commits_count = commitCount(owner,repo_name)

		return commits_count, last_commit_date, contributors

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

def process(repo_url,light=True):

	# path de ce fichier

	git_error = 0
	is_windows = (os.name == 'nt')

	# vérifie que les dir tmp et deps existent sinon les crées
	tmp = 'tmp'
	if not os.path.exists(tmp):
		os.makedirs(tmp)
	else :
		deleteDir(tmp)
		os.makedirs(tmp)

	deps = 'deps'
	if not os.path.exists(deps):
		os.makedirs(deps)
	else :
		deleteDir(deps)
		os.makedirs(deps)

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
		exit(1) # todo voir quoi faire

	tags = [tag.name for tag in repo.tags]

	for tag in tags :

		print(f'\tAnalyse de la version {tag}')

		try :

			repo.git.checkout(tag,force=True)	

			depsfile = os.path.join(deps,repo_name[:-3] + '_' + tag + '.json')

			if tag == '0' : # Sinon les fichiers ne sont pas dans l'ordre
				depsfile = os.path.join(deps,repo_name[:-3] + '_' + tag + '.0.json')
			elif tag == 'null' : # ne possède pas de version
				continue

			try:
				# npm ci (installe toutes les dépendances)
				subprocess.run(['npm', 'ci'],shell=is_windows, cwd=repo_path,capture_output=True)
			except subprocess.CalledProcessError as e:
				print(f'Erreur lors de l\'exécution de npm ci : {e}')

			try :
				# npm list -all -json > alldeps.json (création du fichier avec toutes les dépendances)
				
				result = subprocess.run(['npm', 'list', '--all', '--json'], cwd=repo_path,text=True,capture_output=True,shell=is_windows)
				deps_dict = json.loads(result.stdout)

			except subprocess.CalledProcessError as e:
				print(f'Erreur lors de la création de depsfile : {e}')
			try :
				# rm -rf node_modules (supprime les dépendances = annule npm ci)
				subprocess.run(['rm', '-rf','node_modules'], shell=is_windows, cwd=repo_path,capture_output=True)
			except subprocess.CalledProcessError as e:
				print(f'Erreur lors de l\'annulation de npm ci : {e}')

			deps_dict.pop('problems',None)

			api_data=[0,0,[]]
			files_data = 0,0

			if not light : # pour éviter de spam l'api github et de compter tous les fichiers
				try :
					api_data = get_data(repo_url) 
				except :
					api_data=[0,0,[]]
					print(f'Erreur avec l\'api git pour la version {tag} : {e}')

				files_data = count_files(repo_path)

			depNb = count_dependencies(deps_dict)

			commit = repo.tags[tag].commit
			release_date = commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')

			data_json = {
				"release_date": release_date,
				"commit_count": api_data[0],
				"last_commit_date": api_data[1],
				"contributor_count": len(api_data[2]),
				"contributors": api_data[2],
				"dependencies_count" : depNb,
				"js_file_count": files_data[0],
				"json_file_count": files_data[1]
			}

			deps_dict.update(data_json) 

			with open(depsfile,'w') as file :
				json.dump(deps_dict,file,indent=4)
	
		except Exception as e:
			print(f'Erreur lors de l\'analyse de la version {tag} : {e}')
			git_error+=1

	repo.close()
	deleteDir(repo_path)

	print(f'Nombre de versions non analysées car error: {git_error}')

