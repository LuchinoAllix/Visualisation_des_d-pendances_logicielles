import json
import os
import pandas as pd
import matplotlib.pyplot as plt

def analyse(tree, depth=0, widths=None,nodes=[0]):
    nodes[0]+=1
    if widths is None:
        widths = {}
    
    if depth in widths:
        widths[depth] += 1
    else:
        widths[depth] = 1

    max_depth = depth

    if isinstance(tree, dict):
        for key,value in tree.items() :
            current_depth = analyse(value,depth+1,widths,nodes)[0]
            max_depth = max(max_depth,current_depth)
    elif isinstance(tree, list):
        for item in tree :
            current_depth = analyse(item,depth+1,widths,nodes)[0]
            max_depth = max(max_depth,current_depth)
        
    return max_depth,widths,nodes

def getData(path):
    with open(path,'r') as file :
        json_data = json.load(file)
    data = analyse(json_data)
    return data[0],max(data[1].values()),data[2][0]

if __name__ == "__main__": 
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path,"deps")
    depth = []
    width = []
    nodes = []
    dates = []
    versions = []
    for dir in os.walk(path) :
        for subdir in dir[2] :
            data = getData(os.path.join(dir[0],subdir))
            depth.append(data[0])
            width.append(data[1])
            nodes.append(data[2])

            with open(os.path.join(dir[0],subdir),'r') as file :
                json_data = json.load(file)
            dates.append(json_data["release_date"])
            versions.append(json_data["version"])
    
        plt.bar(versions,depth)
        plt.title("Profondeur de l'arbre pour chaque version")
        plt.xlabel('Version')
        plt.ylabel('Profondeur')
        plt.xticks(rotation=45,fontsize=6)
        plt.show()

        plt.bar(versions,width)
        plt.title("Largeur de l'arbre pour chaque version")
        plt.xlabel('Version')
        plt.ylabel('Largeur')
        plt.xticks(rotation=45,fontsize=6)
        plt.show()

        plt.bar(versions,nodes)
        plt.title("Nombre de noeuds dans l'arbre par version")
        plt.xlabel('Version')
        plt.ylabel('Nombre de noeuds')
        plt.xticks(rotation=45,fontsize=6)
        plt.show()

        valid_dates = pd.to_datetime(dates)
        data = pd.DataFrame({'Date': valid_dates, 'Version': versions})
        data = data.sort_values(by='Date')

        plt.scatter(data['Date'], data['Version'])
        plt.xlabel('Date')
        plt.ylabel('Version')
        plt.title('Répartition des versions au cours du temps')
        plt.yticks(rotation=0,fontsize=6)
        plt.show()
