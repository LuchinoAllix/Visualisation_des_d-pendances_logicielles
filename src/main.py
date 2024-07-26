from fetch import process
from time import time
from sys import argv
from convert import convert

if __name__ == "__main__" :

	# Projets à analyser par défault
	project_url = "https://github.com/processing/p5.js"
	light = False

	if len(argv) == 1 :
		pass
	elif len(argv) == 2 :
		project_url = argv[1]
	else :
		project_url == argv[1]
		light = True

	start = time()
	process(project_url,light)
	print(f'Temps total d\'analyse : {(time()-start) / 60} minutes')

	convert()