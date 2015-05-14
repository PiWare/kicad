#!/usr/bin/python

import fp
from fpgen import *
import csv
import argparse
import config
cfg = config.Config("config")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'Footprint generator from csv table.')
	parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
	parser.add_argument('--output_path', metavar = 'output_path', type = str, help = 'Output path for generated KiCAD footprint files', required = True)
	args = parser.parse_args()

	with open(args.csv, 'rb') as csvfile:
		table = csv.reader(csvfile, delimiter=',', quotechar='\"')
		first_row = 1
		for row in table:
			if first_row == 1:
				header = row
				first_row = 0
			else:
				data = dict(zip(header, row))
				# Can this be made little bit more elegant?
				for key in data:
					try:
						if key.find("count") != -1:
							data[key] = int(data[key])
						else:
							data[key] = float(data[key])
					except:
						pass

				generator = data['generator']
				del data['generator']

				if generator in fp.registry.keys():
					gen = fp.registry[generator](**data)

					output = open(args.output_path+'/'+data['name']+cfg.FOOTPRINT_EXTENSION, "w")
				#	print fp.render()
					output.write(gen.render())
					output.close()
					del gen
				else:
					print "Unknown footprint generator '"+generator+"'"

			#	if generator == "soic":
			#		fp = soic(**data)
			#	elif generator == "dip":
			#		fp = dip(**data)
			#	elif generator == "qfp":
			#		fp = qfp(**data)
			#	elif generator == "wired_resistor":
			#		fp = wired_resistor(**data)
			#	elif generator == "connector_grid_male":
			#		fp = connector_grid_male(**data)
			#	elif generator == "connector_grid_female":
			#		fp = connector_grid_female(**data)

			#	if 'fp' in locals():
			#		output = open(args.output_path+'/'+data['name']+cfg.FOOTPRINT_EXTENSION, "w")
			#	#	print fp.render()
			#		output.write(fp.render())
			#		output.close()
			#		del fp
			#	else:
			#		print "Unknown footprint generator '"+generator+"'"

#print fp.registry
#
#t = fp.registry['base']("name")
#print t.render()
#
#t = fp.registry['wired']("name")
#print t.render()
