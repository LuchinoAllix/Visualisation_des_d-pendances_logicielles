import os
import stat
import shutil

def deleteDir(dossier:str) -> None:
	""" 
	Supprime tout le contenu d'un dossier en changeant les permissions
	
	Args :
		dossier (str) : dossier à supprimer

	Effets de bord :
		Supprime un dossier
	"""
	for root, dirs, files in os.walk(dossier):
		for dir in dirs:
			os.chmod(os.path.join(root, dir), stat.S_IRWXU)
		for file in files:
			os.chmod(os.path.join(root, file), stat.S_IRWXU)
	
	# Supprime le dossier et tout son contenu
	shutil.rmtree(dossier)

def verify_path(dir:str) -> None:
	""" 
	Vérifie si un dossier existe, si oui le supprime et le crée à nouveau 
	(pour qu'il soit vide), sinon le crée.
	
	Args :
		dir (str) : dossier à crée

	Effets de bord :
		Supprime et créer un dossier
	"""
	if not os.path.exists(dir):
		os.makedirs(dir)
	else :
		deleteDir(dir)
		os.makedirs(dir)