import json
import os
from normalize import normalize
from tools import verify_path
import matplotlib.pyplot as plt

def addToDico(name:str,color:str,dico:dict)->str:
    """ 
	Retourne la couleur associé à une dependance dans le dictionnaire de gestion
    des couleurs, si la dépendance est déjà présente, on retourne la couleur,
    sinon on ajoute la nouvelle couleur fournie.
	
	Args :
		name (str) : nom de la dépendance
        color (str) : couleur associée à la nouvelle dépendance
        dico (dict) : dictionnaire d'assocition des couleurs aux dependances

    Returns : 
        str : la couleur associée à la dépendance

	Effets de bord :
		modifie le dictionnaire
	"""
    if name in dico :
        return dico[name]
    else :
        dico[name]= color
        return color

def convert_to_tree_version(name:str, dependency:dict,color:str,dico:dict)->dict:
    """ 
	Fonction recursive pour transformer un arbre de dépendances en arbre
    visualisable avec d3 en incorporant la couleur en fonction des version
    des dépendances
	
	Args :
		name (str) : nom de la dépendance
        dependency (dict) : dictionnaire de l'arbre des dépendances
        color (str) : couleur à ajouter
        dico (dict) : dicionnaire des dep -> couleur

    Return :
        dict : dictionnaire des noeuds visualisable

	Effet de bord :
		modifie le dictionnaire des couleur
	"""
    if "version" not in dependency :
        new_color = addToDico(name,color,dico)
    else :
        new_color = addToDico(name+dependency["version"],color,dico)
        name=name+'-'+dependency['version']

    node = {
        "name": name,
        "value": 10, 
        "type": new_color,
        "level": new_color,  
        "children": []
    }
    
    if "dependencies" in dependency:
        for dep_name, dep_info in dependency["dependencies"].items():
            child_node = convert_to_tree_version(dep_name, dep_info,color,dico)
            node["children"].append(child_node)
    
    if not node["children"]:
        del node["children"]
    
    return node

def convert_to_tree_data(name:str, dependency:dict,color_scale:[str],choice)->dict: # type: ignore
    """ 
	Fonction recursive pour transformer un arbre de dépendances en arbre
    visualisable avec d3 en incorporant la couleur en fonction d'une echelle'
	
	Args :
		name (str) : nom de la dépendance
        dependency (dict) : dictionnaire de l'arbre des dépendances
        color_scale ([str]) : liste des couleur à ajouter
        dico (dict) : dicionnaire des dep -> couleur

    Return :
        dict : dictionnaire des noeuds visualisable

	Effet de bord :
		modifie le dictionnaire des couleur
	"""
    if choice not in dependency :
        dependency[choice] = 0
        
    color = color_scale[int(dependency[choice])]
    node = {
        "name": name,
        "value": 10, 
        "type": color,
        "level": color,  
        "children": []
    }
    
    if "dependencies" in dependency:
        for dep_name, dep_info in dependency["dependencies"].items():
            child_node = convert_to_tree_data(dep_name, dep_info,color_scale,choice)
            node["children"].append(child_node)
    
    if not node["children"]:
        del node["children"]
    
    return node

def generate_colors(v_total:int)->[str]: # type: ignore
    """ 
	Créer une échelle de couleur en fonction de v_total
	
	Args :
		v_total (int) : nombre de couleurs voulue

    Return :
        [str] : liste de couleurs format rgba

	"""
    cmap = plt.cm.get_cmap('plasma', v_total)
    colors = [cmap(i) for i in range(v_total)]
    return [f"rgba({int(r*255)},{int(g*255)},{int(b*255)},{a})" for r, g, b, a in colors]

def convert()->None:
    """ 
	Fonction principale, crée des arbres visualisable pour d3 à partir 
    des arbres de dépendances.

	Effet de bord :
		Créer des fichiers pour la visualisation des arbres (json et css)
	"""
    
    print("Conversion des données en arbres")
    
    with open(os.path.join('deps','version-date.json'),'r') as file :
        version_date = json.load(file)
        file.close()

    dirs_version = version_date.keys()
    dirs_date = sorted(version_date, key=version_date.get)

    nbcommit, nbcontributors = getMaxNbCommitAndNbContributors()

    # crée les échelles de couleur
    colors_version = generate_colors(len(dirs_version))
    colors_commit = generate_colors(nbcommit+1)
    colors_contributors = generate_colors(nbcontributors+1)

    dataFields = ['version','commit','contributors']
    colors = [colors_version,colors_commit,colors_contributors]

    # crée les arbres et les fichiers qui les relients entre eux     
    fun('v',dirs_version,colors)
    fun('d',dirs_date,colors)

    # crée les fichiers css 
    for i in range(len(dataFields)):
        make_CSS(colors[i],dataFields[i])

def fun(type:str,dirs:[str],colors:[str]) -> None: # type: ignore
    """ 
	Fonction qui crée les fichiers avec les données visualisables 
	
	Args :
		type (str) : type de tri (v:version, d:date)
        dirs ([str]) : liste des fichier des dépendances
        colors ([str]) : échelle de couleur

	Effet de bord :
		Crée les fichiers visualisable ainsi que ceux qui leur donne un ordre
	"""
    dico_colors={}
    dataFields = ['version','commit','contributors']
    paths = {'version':[],'commit':[],'contributors':[]}
    cnt = 0
    for field in dataFields : # crée les dossier
        verify_path(os.path.join('Visualisation','trees',field+'_'+type))
    for dir in dirs : # pour chaque fichier de deps on crée les fichiers visualisables
        v = dir.split('_')[-1].split('.json')[0]
        with open(dir, 'r') as file:
            data = json.load(file)
            file.close()
        try :
            root_name = data["name"]
        except :
            root_name = "null"
        root_dependency = data["dependencies"]
        for field in dataFields :

            if field == 'version':
                
                tree = convert_to_tree_version(root_name, {"dependencies": root_dependency},str(colors[0][cnt]),dico_colors)
                cnt+=1
            else :
                tree = convert_to_tree_data(root_name, {"dependencies": root_dependency},colors[1],'commit_count')

            try :
                tree['version'] = data['version']
            except :
                tree['version'] = "null"

            tree['date'] = data['release_date']
            tree['dir'] = v
            tree['maxCommit'] = len(colors[1])
            tree['maxContributors'] = len(colors[2])
            tree['nbVersion'] = len(colors[0])

            if type == 'v':
                file_path = os.path.join('trees',field+ '_'+type,v+'.json')
            else :
                file_path = os.path.join('trees',field+'_'+type,tree['date']).replace(':','-') +'.json'
            paths[field].append(file_path)
            with open(os.path.join('Visualisation',file_path),'w') as file :
                json.dump(tree, file, indent=4)
                file.close()
    for field in dataFields :
        with open(os.path.join('Visualisation','trees','paths_'+field+'_'+type+'.json'),'w') as file :
            json.dump(paths[field],file,indent=4)
            file.close()

def make_CSS(rgba_colors:[str],name:str)->None : # type: ignore
    """ 
	Crée les fichier css avec l'echelle de couleur
	
	Args :
        rgba_colors ([str]) : liste des couleurs
		name (str) : nom du fichier

	Effet de bord :
		Crée les fichiers
	"""
    gradient_stops = ', '.join(rgba_colors)

    css_content = f""" 
        .color-gradient {{
            width: 100%;
            height: 50px;
            background: linear-gradient(to right, {gradient_stops}); 
        }} """

    # Write the CSS content to a file
    with open(os.path.join('Visualisation','trees',"colors_"+name+".css"), "w") as file:
        file.write(css_content)

def getMaxNbCommitAndNbContributors()->None:
    """ 
	Pour avoir le maximum de nombre de commit et de contribueur dans les fichiers
    de dépendances

    Return :
        (int, : nombre maximum de commits
         int) : nombre maximum de contributeurs

	"""
    dirs = sorted(os.walk('deps'),key=lambda x:x[2])
    maxes = [0,0]
    for subdir in dirs[0][2] :
        with open(os.path.join('deps',subdir), 'r') as file:
            deps_dico = json.load(file)
            file.close()
        getMaxNbCommitAndNbContributorsRec(deps_dico,maxes)
    return maxes

def getMaxNbCommitAndNbContributorsRec(deps_dico:dict,maxes:(int,int))->None: # type: ignore
    """ 
	fonciton recursive Pour avoir le maximum de nombre de commit et de contribueur 
    dans un arbre de dépendances

    Args :
        deps_dico (dict) : dictionnaire des dépendances
        maxes (int,int) : meilleure valeur jusqu'à présent

	"""
    if 'commit_count' in deps_dico :
        nb_commits = deps_dico['commit_count']
        if  int(nb_commits) > maxes[0] :
            maxes[0] = int(nb_commits)
    if 'contributor_count' in deps_dico :
        nb_contributors = deps_dico['contributor_count']
        if  int(nb_contributors) > maxes[1] :
            maxes[1] = int(nb_contributors)
    if "dependencies" in deps_dico :
        for _, dep in deps_dico['dependencies'].items():
            getMaxNbCommitAndNbContributorsRec(dep,maxes)
    
if __name__ == "__main__":
    convert()
    normalize()

