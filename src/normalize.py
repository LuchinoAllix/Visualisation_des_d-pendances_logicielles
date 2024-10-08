import os
import json

def normalize() -> None:
	""" 
	Fait en sorte que les arbres aient tous la même hauteur

	Effets de bord :
		Modifie les dossiers avec les arbres
	"""

	print("Normalisation de la taille des arbres")

	treeDir = os.path.join('Visualisation','trees','commit_d')
	dirs = sorted(os.walk(treeDir),key=lambda x:x[2])
	maxDepth = 0
	depths = {}
	
	# Calcul la plus haute taille parmis tous les arbres
	for subdir in dirs[0][2] :
		with open(os.path.join(treeDir,subdir), 'r') as file:
			tree = json.load(file)
			file.close()
		depth = get_depth(tree)
		depths[subdir] = depth
		maxDepth = max(maxDepth,depth)
	
	treeDir = os.path.join('Visualisation','trees')
	dirs = [nom for nom in os.listdir(treeDir) if os.path.isdir(os.path.join(treeDir, nom))]
	
	for dir in dirs:
		for file_name in os.listdir(os.path.join(treeDir,dir)) :
			
			with open(os.path.join(treeDir,dir,file_name), 'r') as file:
				tree = json.load(file)
				file.close()

			deepen(tree,maxDepth)
				
			with open(os.path.join(treeDir,dir,file_name), 'w') as file:
				json.dump(tree, file, indent=2)
				file.close()


def get_depth(dico:dict)->int:
	""" 
	Retourne la profondeur d'un arbre
	
	Args :
		dico (dict) : arbre à analyser

	Returns :
		int : la profondeur de l'arbre
	"""
	if "children" not in dico or not dico["children"]:
		return 1
	else:
		return 1 + max(get_depth(child) for child in dico["children"])

def deepen(dico:dict,amount:int)->None:
	""" 
	Augmente la profndeur d'un arbre d'une certaine valeur
	
	Args :
		dico (dict) : l'arbre à modifier

	Effets de bord :
		modifie l'arbre
	"""
	current_node = dico
	for _ in range(amount):
		new_node = {
			"name": "empty",
			"value": 0, 
			"type": "white",  
			"level": "white",  
			"children": []
    	}
		current_node["children"].append(new_node)
		current_node = new_node
	
