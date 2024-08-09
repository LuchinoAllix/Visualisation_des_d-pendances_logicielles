import os
import stat
import shutil

def deleteDir(dossier):
	# Fonction pour changer les permissions de tous les fichiers dans le dossier
	for root, dirs, files in os.walk(dossier):
		for dir in dirs:
			os.chmod(os.path.join(root, dir), stat.S_IRWXU)
		for file in files:
			os.chmod(os.path.join(root, file), stat.S_IRWXU)
	
	# Supprime le dossier et tout son contenu
	shutil.rmtree(dossier)

def verify_path(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)
	else :
		deleteDir(dir)
		os.makedirs(dir)