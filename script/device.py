#!/usr/bin/python
#
# Copyright (c) 2015 Benjamin Fueldner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# Generate device files from csv table

import re
import csv
import config
import argparse
import string
import os

cfg = config.Config("config")

class device():
	"Device base class"

class template(device):
	""

	format = "#\n# %s\n#\n$CMP %s\nD %s\nK %s\nF %s\n$ENDCMP\n"

	def __init__(self, filename):
		file = open(filename, "r")
		self.data  = file.read()
		file.close()

		# Remove header and comments
		self.data = re.sub('^#.*$\s*', '', re.sub('^EESchema.*$\s*', '', self.data, 0, re.M), 0, re.M)

		self.map = {}
	#	self.map["DEVICE"] = "Resistor"
	#	self.map["VALUE"] = "10k"

	def add(self, **kwargs):
		for key, value in kwargs.iteritems():
			self.map[key.upper()] = value

	def render(self):
		self.data = "#\n# " + self.map['NAME'] + "\n#\n" + self.data
		return re.sub("\$(\w+)", lambda m: self.map[m.group(1)] if m.group(1) in self.map else m.group(0), self.data)

	def description(self):
	# EESchema-DOCLIB  Version 2.0
		desc = ""
		if 'DESCRIPTION' in self.map:
			desc += 'D ' + self.map['DESCRIPTION'] + '\n'
		if 'KEYWORDS' in self.map:
			desc += 'K ' + self.map['KEYWORDS'] + '\n'
		if 'DOCUMENT' in self.map:
			desc += 'F ' + self.map['DOCUMENT'] + '\n'

		if len(desc):
			return "#\n# " + self.map['NAME'] + "\n#\n" + desc
		else:
			return ""
	#	return template.format%(self.map['NAME'], self.map['NAME'], self.map['DESCRIPTION'], self.map['KEYWORDS'] if 'KEYWORDS' in self.map else '', self.map['DOCUMENT'] if 'DOCUMENT' in self.map else '')
	#	return '#\n# ' + self.map['NAME'] + '\n#\n$CMP '
	#	#
	#	$CMP 74*05
	#	D Beschreibung
	#	K Keyword
	#	F Name des Dokuments
	#	$ENDCMP

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'Device generator from csv table.')
	parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
	parser.add_argument('--symbol', metavar = 'symbol', type = str, help = 'Output file for generated KiCAD symbols', required = True)
	parser.add_argument('--desc', metavar = 'desc', type = str, help = 'Output file for generated KiCAD symbol description', required = True)
	args = parser.parse_args()

#	print basename(args.csv)
#	print os.path.splitext(os.path.basename(args.csv))[0]

	symbol_output = open(args.symbol, "w")
	symbol_output.write("EESchema-LIBRARY Version 2.3\n")
	desc_output = open(args.desc, "w")
	desc_output.write('EESchema-DOCLIB  Version 2.0\n')
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

				filename = 'data/'+data['symbol']+'.lib'
				del data['symbol']

				tpl = template(filename)
				tpl.add(**data)
				symbol_output.write(tpl.render())
				desc_output.write(tpl.description())

	desc_output.write('#\n#End Doc Library\n')
	desc_output.close()
	symbol_output.write('#\n#End Library\n')
	symbol_output.close()
