#!/usr/bin/python
#
#     Copyright (C) 2015 Thomas Bernard
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>

#     This script is used to generate a summary of kicad footprints and symbols

import re
import os
import config
cfg = config.Config("config")

symbolNameRe = re.compile('F1 +"([^"]+)"')
packageNameRe = re.compile('  \(descr +"([^"]+)"\)')

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Generate q list of parts and footprint of kicad libraries.')
    parser.add_argument('--libs', nargs='+', metavar='libs', type=str,
            help='list of kicad .lib files to scan')
    parser.add_argument('--footprints', nargs='+', metavar='fps', type=str,
            help='list of kicad footprint files to scan')
    parser.add_argument('--output', metavar='out', type=str,
            help='the file containing the summary', required=True)
    args = parser.parse_args()
    output = open(args.output, "w")

    output.write("Symbol summary\n")
    if args.libs != None:
        for src in args.libs:
            output.write("---------------------------------\n")
            output.write("Library file : %s\n"%(src))
            output.write("---------------------------------\n")
            ifile = open(src,"r")
            data = ifile.read()
            ifile.close()
            for match in symbolNameRe.finditer(data):
                output.write(match.group(1)+"\n")

    if args.footprints != None:
        for src in args.footprints:
            output.write("---------------------------------\n")
            output.write("Footprint section '%s'\n"%(src))
            output.write("---------------------------------\n")

            list = os.listdir(src)
            list = natural_sort(list)
            for file in list:
                if file.endswith(cfg.FOOTPRINT_EXTENSION):
                    print(file)

                    ifile = open(src+'/'+file, "r")
                    data = ifile.read()
                    ifile.close()
                    for match in packageNameRe.finditer(data):
                        output.write(match.group(1)+"\n")
