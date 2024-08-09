import json
import os
from normalize import normalize
from tools import verify_path
import matplotlib.pyplot as plt

def addToDico(name,color,dico):
    if name in dico :
        return dico[name]
    else :
        dico[name]= color
        return color

def convert_to_tree_version(name, dependency,color,dico):
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

def convert_to_tree_data(name, dependency,color_scale,choice):

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

def generate_colors(v_total):
    cmap = plt.cm.get_cmap('plasma', v_total)
    colors = [cmap(i) for i in range(v_total)]
    return [f"rgba({int(r*255)},{int(g*255)},{int(b*255)},{a})" for r, g, b, a in colors]

def convert():
    
    print("Conversion des données en arbres")
    
    with open(os.path.join('deps','version-date.json'),'r') as file :
        version_date = json.load(file)
        file.close()

    dirs_version = version_date.keys()
    dirs_date = sorted(version_date, key=version_date.get)

    nbcommit, nbcontributors = getMaxNbCommitAndNbContributors()

    colors_version = generate_colors(len(dirs_version))
    colors_commit = generate_colors(nbcommit+1)
    colors_contributors = generate_colors(nbcontributors+1)

    dataFields = ['version','commit','contributors']
    colors = [colors_version,colors_commit,colors_contributors]
    
    fun('v',dirs_version,colors)
    fun('d',dirs_date,colors)

    for i in range(len(dataFields)):
        make_CSS(colors[i],dataFields[i])

def fun(type,dirs,colors):
    dico_colors={}
    dataFields = ['version','commit','contributors']
    paths = {'version':[],'commit':[],'contributors':[]}
    cnt = 0
    for field in dataFields :
        verify_path(os.path.join('Visualisation','trees',field+'_'+type))
    for dir in dirs :
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

def make_CSS(rgba_colors,name) :
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

def getMaxNbCommitAndNbContributors():
    dirs = sorted(os.walk('deps'),key=lambda x:x[2])
    maxes = [0,0]
    for subdir in dirs[0][2] :
        with open(os.path.join('deps',subdir), 'r') as file:
            deps_dico = json.load(file)
            file.close()
        getMaxNbCommitAndNbContributorsRec(deps_dico,maxes)
    return maxes

def getMaxNbCommitAndNbContributorsRec(deps_dico,maxes):
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

