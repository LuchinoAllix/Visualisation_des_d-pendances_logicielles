import os
import subprocess
import json
import requests
import re
import shutil
import stat
import time
from git import Repo

requests_dico_git = {}
requests_dico_npm = {}
requests_git = 0
requests_npm = 0
depProblems = 0

with open('token.txt') as file :
	token = file.readline()
	file.close()

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

def commitCount(u, r, headers):
	# https://gist.github.com/codsane/25f0fd100b565b3fce03d4bbd7e7bf33
	response = requests.get(f'https://api.github.com/repos/{u}/{r}/commits?per_page=1', headers=headers)
	global requests_git
	requests_git+=1
	if 'last' in response.links:
		last_page_url = response.links['last']['url']
		return re.search(r'\d+$', last_page_url).group()
	else:
		return len(response.json())  # Retourne le nombre de commits si pas de lien 'last'

def contributorsList(u, r, headers):
	contributors = []
	page = 1
	while True:
		response = requests.get(f'https://api.github.com/repos/{u}/{r}/contributors', params={'page': page}, headers=headers)
		global requests_git
		requests_git+=1
		try:
			data = response.json()
			if isinstance(data, dict) and 'message' in data:
				# Si la réponse est un dictionnaire avec un message d'erreur
				print(f"Erreur API GitHub: {data['message']}")
				break
			if not data:
				break
			contributors.extend([contributor['login'] for contributor in data])
		except json.JSONDecodeError:
			# Si la réponse n'est pas un JSON valide
			print(f"Erreur de décodage JSON pour {u}/{r} page {page}")
			break
		page += 1
	return contributors

def get_data(repo_url):
	if len(repo_url)==0 :
		return 0,0,[]

	
	headers = { "Authorization": f"token {token}"}

	if repo_url in requests_dico_git :
		return requests_dico_git[repo_url]

	# Extraire le nom du propriétaire et le nom du repo à partir de l'URL
	# Exemple d'URL : https://github.com/processing/p5.js
	parts = repo_url.strip('/').split('/')
	owner = parts[-2]
	repo_name = parts[-1]

	last_commit_date = 0
	contributors = []
	commits_count = 0

	try:
		commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
		response_commits = requests.get(commits_url,headers=headers)
		global requests_git
		requests_git+=1
		response_commits.raise_for_status()  # Lève une exception pour les erreurs HTTP
		last_commit_date = response_commits.json()[0]['commit']['author']['date']

		rate_remaining = int(response_commits.headers.get('X-RateLimit-Remaining'))
		rate_reset = int(response_commits.headers.get('X-RateLimit-Reset'))

		if rate_remaining < 50:
			# Calculer le temps à attendre jusqu'à la réinitialisation
			sleep_time = rate_reset - int(time.time())
			print(f"Nombre de requêtes restant est inférieur à 50. Attente de {sleep_time/60} minutes jusqu'à la réinitialisation.")
			time.sleep(sleep_time + 10)  # 10 secondes de marge de sécurité

	except Exception as e:
		print(f"Erreur lors de la récupération des données pour la date de dernier commit :\n \t{e}")

	try :
		contributors = contributorsList(owner,repo_name,headers)
	except Exception as e:
		print(f"Erreur lors de la récupération des données pour la liste des contributeurs de {repo_url}: {e}")

	try :
		commits_count = commitCount(owner,repo_name,headers)
	except Exception as e:
		print(f"Erreur lors de la récupération des données pour le nombre de commits de {repo_url}: {e}")

	data = commits_count, last_commit_date, contributors
	requests_dico_git[repo_url] = data
	
	return data

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

def verify_path(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)
	else :
		deleteDir(dir)
		os.makedirs(dir)

def process(repo_url):

	git_error = 0
	is_windows = (os.name == 'nt')

	# vérifie que les dir tmp et deps existent sinon les crées
	tmp = 'tmp'
	verify_path(tmp)
	deps = 'deps'
	verify_path(deps)

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

	tags = [tag.name for tag in repo.tags]

	# dictionnaire qui relie chaque version à sa date de release
	version_date = {} 

	for tag in tags :

		print(f'\tAnalyse de la version {tag}')
		start = time.time()

		try :

			repo.git.checkout(tag,force=True)	

			depsfile = os.path.join(deps,repo_name[:-3] + '_' + tag + '.json')

			if tag == '0' : # Sinon les fichiers ne sont pas dans l'ordre
				depsfile = os.path.join(deps,repo_name[:-3] + '_' + tag + '.0.json')
			elif tag == 'null' : # ne possède pas de version
				continue

			try:
				# npm ci (installe toutes les dépendances)
				print('\tTéléchargement des dépendances')
				subprocess.run(['npm', 'ci'],shell=is_windows, cwd=repo_path,capture_output=True)
			except subprocess.CalledProcessError as e:
				print(f'Erreur lors de l\'exécution de npm ci : {e}')

			try :
				# npm list -all -json > alldeps.json (création du fichier avec toutes les dépendances)
				print('\tExportation des dépendances')
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

			api_data = get_data(repo_url) 

			files_data = count_files(repo_path)

			depNb = count_dependencies(deps_dict)

			commit = repo.tags[tag].commit

			release_date = commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')

			version_date[depsfile]=release_date

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

			enrich(deps_dict)

			with open(depsfile,'w') as file :
				json.dump(deps_dict,file,indent=4)
			
		except Exception as e:
			print(f'Erreur lors de l\'analyse de la version {tag} : {e}')
			git_error+=1

		print(f'\t -> time taken : {(time.time()-start)/60}')

	repo.close()
	deleteDir(repo_path)

	with open(os.path.join(deps,'version-date.json'),'w') as file :
		json.dump(version_date,file,indent=4)
		file.close()

	deleteDir(tmp)

	global requests_npm
	global requests_git

	print('\nDonnées d\'analyse :')
	print(f'Nombre de requête à git : {requests_git}')
	print(f'Nombre de requête à npm : {requests_npm}')
	print(f'Nombre de versions non analysées car error: {git_error}')
	print(f'Nombre de problèmes rencontré avec l\'obtention de données git : {depProblems}')

def get_github_repo_url(package_name,version=None):
	if version :
		url = f"https://registry.npmjs.org/{package_name}/{version}"
	else :
		url = f"https://registry.npmjs.org/{package_name}"

	if url in requests_dico_npm :
		return requests_dico_npm[url]

	response = requests.get(url)
	global requests_npm
	requests_npm+=1

	if response.status_code == 200:
		data = response.json()
		try :
			repo_url = data.get('repository', {}).get('url', '')

			if len(repo_url)==0:
				raise Exception
		
			if repo_url.startswith('git+ssh'):
				repo_url = repo_url.replace('git+ssh://git@github.com', 'https://github.com')
			elif repo_url.startswith('git@github.com:'):
				repo_url = repo_url.replace('git@github.com:', 'https://github.com/')
			elif repo_url.startswith('git+'):
				repo_url = repo_url[4:]
			elif repo_url.startswith('git://'):
				repo_url = repo_url.replace('git://', 'https://')
			elif repo_url.startswith('git:'):
				repo_url = repo_url[4:]

			if repo_url.endswith('.git'):
				repo_url = repo_url[:-4]
			elif repo_url.endswith('.git#main'):
				repo_url = repo_url[:-4]

			repo_url = re.sub(r'/tree/.*', '', repo_url)
			requests_dico_npm[url]=repo_url
			return repo_url
		except :
			print(f'No URL found in {package_name}/{version}')
			requests_dico_npm[url] = ""
			return ""
	else:
		requests_dico_npm[url] = ""
		print(f"Failed to get GitHub URL for {package_name}")
		return ""

def enrich(deps_dict):
	print('\tTéléchargement des données supplémentaire des dépendances')
	if "name" not in deps_dict :
		root_name="null"
	else :
		root_name = deps_dict["name"]
	root_dependency = deps_dict["dependencies"]
	enrichRec(root_name, {"dependencies": root_dependency})

def enrichRec(name,deps_dict):
	try :
		version = None
		if "version" in deps_dict :
			version = deps_dict["version"]
		url = get_github_repo_url(name,version)
		data = get_data(url)
	except Exception as e :
		global depProblems
		depProblems += 1
		print(f"Error in getting data for package {name} :\n\t{e}")
		data = 0,0,[]
	
	deps_dict["commit_count"] = data[0]
	deps_dict["last_commit_date"] = data[1]
	deps_dict["contributor_count"] = len(data[2])
	deps_dict["contributors"] = data[2]

	if "dependencies" in deps_dict:
		for dep_name, dep_info in deps_dict["dependencies"].items():
			enrichRec(dep_name,dep_info)
