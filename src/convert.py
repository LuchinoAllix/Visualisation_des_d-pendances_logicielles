import json
import os
from fetch import deleteDir

def convert_to_tree(name, dependency):
    node = {
        "name": name,
        "value": 10, 
        "type": "grey",  
        "level": "red",  
        "children": []
    }
    
    if "dependencies" in dependency:
        for dep_name, dep_info in dependency["dependencies"].items():
            child_node = convert_to_tree(dep_name, dep_info)
            node["children"].append(child_node)
    
    if not node["children"]:
        del node["children"]
    
    return node

def convert():

    treeDir = 'trees'
    if not os.path.exists(treeDir):
        os.makedirs(treeDir)
    else :
        deleteDir(treeDir)
        os.makedirs(treeDir)

    for dir in os.walk('deps') :
            for subdir in dir[2] :
                with open(os.path.join(dir[0],subdir), 'r') as file:
                    data = json.load(file)

                    root_name = data["name"]
                    root_dependency = data["dependencies"]
                    
                    tree = convert_to_tree(root_name, {"dependencies": root_dependency})
                    
                    with open(os.path.join(treeDir, subdir), 'w') as file:
                        json.dump(tree, file, indent=2)

if __name__ == "__main__":
    convert()
