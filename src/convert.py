import json
import os
from fetch import deleteDir
from normalize import normalize
import matplotlib.pyplot as plt

dico = {}

def addToDico(name,color):
    if name in dico :
        return dico[name]
    else :
        dico[name]= color
        return color

def convert_to_tree(name, dependency,color):
    new_color = addToDico(name,color)
    node = {
        "name": name,
        "value": 10, 
        "type": new_color,  
        "level": new_color,  
        "children": []
    }
    
    if "dependencies" in dependency:
        for dep_name, dep_info in dependency["dependencies"].items():
            child_node = convert_to_tree(dep_name, dep_info,color)
            node["children"].append(child_node)
    
    if not node["children"]:
        del node["children"]
    
    return node

def generate_colors(v_total):
    cmap = plt.cm.get_cmap('plasma', v_total)
    return [cmap(i) for i in range(v_total)]

def convert():

    treeDir = os.path.join('Visualisation','trees')
    if not os.path.exists(treeDir):
        os.makedirs(treeDir)
    else :
        deleteDir(treeDir)
        os.makedirs(treeDir)

    dirs = sorted(os.walk('deps'),key=lambda x:x[2])

    vtot = len(dirs[0][2])
    colors = generate_colors(vtot)
    rgba_colors = [f"rgba({int(r*255)},{int(g*255)},{int(b*255)},{a})" for r, g, b, a in colors]
    cnt = 0
    paths =[]
    
    for subdir in dirs[0][2] :
        with open(os.path.join('deps',subdir), 'r') as file:
            data = json.load(file)
            file.close()

        root_name = data["name"]
        root_dependency = data["dependencies"]
        
        tree = convert_to_tree(root_name, {"dependencies": root_dependency},str(rgba_colors[cnt]))
        cnt+=1
        
        try :
            tree['version'] = data['version']
        except :
            tree['version']= 'null'
        
        tree['date'] = data['release_date']
        tree['dir'] = subdir

        filename = data['release_date'].replace(':','-') +'.json'
        path = os.path.join(treeDir,filename)
        paths.append(os.path.join('trees',filename))
        with open(path, 'w') as file:
            json.dump(tree, file, indent=4)
            file.close()

    with open(os.path.join('Visualisation','paths.json'),'w') as file :
        json.dump(paths,file,indent=4)
        file.close()
    
    make_CSS(rgba_colors)

def make_CSS(rgba_colors) :
    gradient_stops = ', '.join(rgba_colors)

    css_content = f""" 
        .color-gradient {{
            width: 100%;
            height: 50px;
            background: linear-gradient(to right, {gradient_stops}); 
        }} """

    # Write the CSS content to a file
    with open(os.path.join('Visualisation',"colors.css"), "w") as file:
        file.write(css_content)

if __name__ == "__main__":
    convert()
    normalize()

