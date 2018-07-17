import sys
import csv
import random

if __name__=='__main__':
	# arg 1 = nome do arquivo com os dados
	# arg 2 = quantidade de dados pretendidos para cada classe
	base = sys.argv[1]
	limit = int(sys.argv[2])
	with open('selection_'+base.split('/')[-1], 'w') as output:
		output = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
		selection = []
		with open(base, 'r') as input:
			input = list(csv.reader(input))
			data = list(input)
			classes = set(x[0] for x in data)
			for c in classes:
				tmp = random.sample([t for t in input if t[0]==c], k=limit)
				selection += tmp

		output.writerows(selection)