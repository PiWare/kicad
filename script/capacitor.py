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

#     This script is used to flatten an avx style capacitor table which can
#     be used by the kicad template scripts
#     The script expects a csv with the following format
#       Thickness, A, B, etc...
#                , 0.33, 0.44, etc...
#       Package, 0101, 0201...
#       WVDC, 10, 10, 16 ...
#       100pF, A, A, ...
#       ...
#
#     The capacitor values are provided in the first column. Each cell which
#     references a package thickness value is considered a valid combination.



import csv
#import itertools

def MakeCondensatorSet(inFile, outFile):
    """ Output a new capacitor set in the outFile.
    """
    parts = {}
    with open(inFile, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        thicknessNames = reader.next()
        thicknessValues = reader.next()
        thickness = dict(zip(thicknessNames[1:],thicknessValues[1:]))
        packageList = reader.next()[1:]
        voltage = reader.next()[1:]
        for row in reader:
            value = row[0]
            for thick,WVDC,pkg in zip(row[1:],voltage,packageList):
                if thick != "":
                    partId = "%s%s%s"%(value,WVDC,pkg)
                    if not partId in parts:
                        outFile.write("capacitor,capacitor_%s_%s_chip_capacitor_%sV,C,chip_capacitor_%s,Capacitor %s 5%% %sV,\"capacitor,smd\",1,2,%s,5%%,%sV"%(value,WVDC,pkg,pkg,value,WVDC,value,WVDC))
                        outFile.write( "\n" )
                        parts[partId] = True




if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--data', nargs='+', metavar='data', type=str,
            help='list of csv files containing pin lists producing capacitor symbols')
    parser.add_argument('--output', metavar='out', type=str,
            help='the flat condensator table file', required=True)
    args = parser.parse_args()
    output = open(args.output, "w")
    # write the header
    output.write("symbol,name,reference,footprint,description,keywords,1,2,value,tolerance,voltage\n")

    if args.data != None:
        for src in args.data:
            MakeCondensatorSet(src, output)
