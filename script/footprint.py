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
# Generate footprint files from csv table

import fp
from fp import cfg
from fpgen import *
import csv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Footprint generator from csv table.')
    parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
    parser.add_argument('--output_path', metavar = 'output_path', type = str, help = 'Output path for generated KiCAD footprint files', required = True)
    args = parser.parse_args()

#   print fp.registry
#   for fop in fp.registry.values():
#       print fop
#       print fop.__doc__

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
                    output.write(gen.render())
                    output.close()
                    del gen
                else:
                    print "Unknown footprint generator '"+generator+"'"
