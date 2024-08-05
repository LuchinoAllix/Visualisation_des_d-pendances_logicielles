from fetch import process
from time import time
from sys import argv
from convert import convert
from normalize import normalize

if __name__ == "__main__" :
	p_start=time()

	# Projets à analyser par défault
	project_url = "https://github.com/Tonejs/Tone.js"

	if len(argv) > 1 :
		project_url = argv[1]

	start = time()
	process(project_url)
	print(f'Temps total d\'analyse : {(time()-start) / 60} minutes\n')

	start = time()
	convert()
	normalize()
	print(f'Temps total de conversion en arbres : {(time()-start) / 60} minutes\n')

	print(f'\nTemps total du programme : {(time()-p_start) / 60} minutes')

