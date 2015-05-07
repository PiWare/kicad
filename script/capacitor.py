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

#     This script is used to generate a kicad symbols for a matrix of capacitors.
#     The script expect a csv with the following format
#       Thickness, A, B, etc...
#                , 0.33, 0.44, etc...
#       Package, 0101, 0201...
#       WVDC, 10, 10, 16 ...
#       100pF, A, A, ...
#       ...
#
#     The capacitor values are provided in the first column. Each cell which
#     references a package thickness value is considered a valid combination and a symbol will be generated



import csv
import itertools
import string
import config
from symbol import *

class Capacitor(object):
    defLine = "DEF %s C 0 10 N Y 1 F N"
    f0Field = """F0 "%%s" %i %i %i H V L CNN"""%(cfg.SYMBOL_NAME_SIZE/2,cfg.SYMBOL_TEXT_MARGIN,cfg.SYMBOL_NAME_SIZE)
    f1Field = """F1 "%%s" %i %i %i H V L CNN"""%(cfg.SYMBOL_NAME_SIZE/2,-cfg.SYMBOL_TEXT_MARGIN,cfg.SYMBOL_NAME_SIZE)

    def __init__(self, value, voltage, polarized):
        self.value = value
        self.voltage = voltage
        self.polarized = polarized
        self.name = "C_%s_%sV"%(self.value,self.voltage)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def getRep(self,packageList):
        if self.polarized:
            secondSide = "P 2 0 1 %i %i %i %i %i N"%(cfg.SYMBOL_LINE_WIDTH,cfg.SYMBOL_NAME_SIZE*-1.2,-cfg.SYMBOL_NAME_SIZE/2,cfg.SYMBOL_NAME_SIZE*1.2,-cfg.SYMBOL_NAME_SIZE/2)
        else:
            secondSide = "P 2 0 1 %i %i %i %i %i N"%(cfg.SYMBOL_LINE_WIDTH,cfg.SYMBOL_NAME_SIZE*-1.2,-cfg.SYMBOL_NAME_SIZE/2,cfg.SYMBOL_NAME_SIZE*1.2,-cfg.SYMBOL_NAME_SIZE/2)
        result = [
            Capacitor.defLine%(string.replace(self.name,",","_")),
            Capacitor.f0Field%(self.name),
            Capacitor.f1Field%(self.name),
            "$FPLIST"]
        result.extend(map(lambda x : "SMDC"+x[0] , packageList))
        result = result + [
            "$ENDFPLIST",
            "DRAW",
            secondSide,
            "P 2 0 1 %i %i %i %i %i N"%(cfg.SYMBOL_LINE_WIDTH,cfg.SYMBOL_NAME_SIZE*-1.2,cfg.SYMBOL_NAME_SIZE/2,cfg.SYMBOL_NAME_SIZE*1.2,cfg.SYMBOL_NAME_SIZE/2),
            Pin("~",1, "P" ).getRep(0,-cfg.SYMBOL_NAME_SIZE/2 -cfg.SYMBOL_PIN_LENGTH,"U",1,1),
            Pin("~",2, "P" ).getRep(0,cfg.SYMBOL_NAME_SIZE/2 + cfg.SYMBOL_PIN_LENGTH,"D",1,1),
            "ENDDRAW",
            "ENDDEF"
        ]
        return result

def MakeCondensatorSet(inFile, outFile):
    """ Output a new capacitor set in the outFile library.
    """
    thickness = {}
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
                if thick!="":
                    part = Capacitor(value,WVDC,False)
                    if part in parts:
                        parts[part].append((pkg,thick))
                    else:
                        parts[part] = [(pkg,thick)]
        for part,pkgList in parts.items():
            outFile.write( string.join(part.getRep(pkgList),"\n" ) )
            outFile.write( "\n" )




if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--data', nargs='+', metavar='data', type=str,
            help='list of csv files containing pin lists producing capacitor symbols')
    parser.add_argument('--output', metavar='out', type=str,
            help='the kicad library output file', required=True)
    args = parser.parse_args()
    output = open(args.output, "w")
    output.write("EESchema-LIBRARY Version 2.3\n")


    if args.data != None:
        for src in args.data:
            MakeCondensatorSet(src, output)
