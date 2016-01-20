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
from math import log,floor,pow
#import itertools

avxVoltageCode = {
    "4" : "4",
"6.3"  : "6" ,
"10"  : "Z" ,
"16"  : "Y" ,
"25"  : "3" ,
"35"  : "D" ,
"50"  : "5" ,
"100"  : "1" ,
"200"  : "2" ,
"500"  : "7"
}
factorMap = {
    "pF": 1,
    "nF": 1000,
    "uF": 1000000
}

decadeMap = {
    0 : "pF",
    1 : "nF",
    2 : "uF"
}

def makeValueCodeAndText(value):
    decimals = floor(log(value)/log(10))
    valueCode = ""
    if decimals <= 0.0:
        valueCode = ("%s"%(value)).replace(".","R")
        valueText = "%s pF"%(value)
    else:
        valueCode = "%i%i"%((int(value) / pow(10,decimals-1)),int( decimals-1))
        base = floor(decimals/3)
        valueText = "%s%s"%(int(value)/pow(10,base*3),decadeMap[base])
    return (valueCode,valueText)

class CapacitorTableGenerator:
    def __init__(self):
        self.parts = {}

    def MakeAVXCondensatorSet(self,inFile):
        """ Output a new capacitor set in the outFile.
        """
        with open(inFile, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            dielectricCode = reader.next()[1]
            thicknessNames = reader.next()
            thicknessValues = reader.next()
            thickness = dict(zip(thicknessNames[1:],thicknessValues[1:]))
            packageList = reader.next()[1:]
            voltage = reader.next()[1:]
            for row in reader:
                value = row[0]
                v = float(value[:-2])*factorMap[value[-2:]]
                valueCode, valueText = makeValueCodeAndText(v)
                for thick,WVDC,pkg in zip(row[1:],voltage,packageList):
                    alias = "%s%s%s%s"%(pkg,avxVoltageCode[WVDC],dielectricCode,valueCode)
                    pkg = "{:0>4}".format(pkg)
                    if thick != "":
                        partId = "capacitor_{:}_{:}_chip_{:}".format(valueText,WVDC,pkg)
                        print partId
                        if not partId in self.parts:
                            self.parts[partId] = ("capacitor,%s,C,chip_capacitor_%s,Capacitor %s 5%% %sV,\"capacitor,smd\",1,2,%s,5%%,%sV"%(partId.replace(" ","_"),pkg,valueText,WVDC,value,WVDC),[alias])
                        else:
                            self.parts[partId][1].append(alias)



    def MakeMurataGRMSerieSet(self,inFile):
        """ Output a new Capacitor set in the outFile.
        """
        inchPkgToCodeMap = {
            "01005" : "02",
            "0201" : "03",
            "0202" : "05",
            "0303" : "08",
            "015015" : "0D",
            "0402" : "15",
            "0603" : "18",
            "02404" : "1U",
            "0805" : "21",
            "1111" : "22",
            "1206" : "31",
            "1210" : "32",
            "1808" : "42",
            "1812" : "43",
            "2220" : "55"
                   }

        mmToInchPkgMap = {
            "0.4x0.2" : "01005",
            "0.6x0.3" : "0201",
            "0.5x0.5" : "0202",
            "0.8x0.8" : "0303",
            "0.38x0.38" : "015015",
            "1.0x0.5" : "0402",
            "1.6x0.8" : "0603",
            "0.6x1.0" : "02404",
            "2.0x1.25" : "0805",
            "2.8x2.8" : "1111",
            "3.2x1.6" : "1206",
            "3.2x2.5" : "1210",
            "4.5x2.0" : "1808",
            "4.5x3.2" : "1812",
            "5.7x5.0" : "2220"
                   }


        voltageMap = {
            "2.5": "0E",
            "4.0": "0G",
            "6.3": "0J",
            "10": "1A",
            "16": "1C",
            "25": "1E",
            "50": "1H",
            "63": "1J",
            "80": "1K",
            "100": "2A",
            "200": "2D",
            "250": "2E",
            "450": "2W",
            "500": "2H",
            "630": "2J",
            "1000": "3A",
            "2000": "3D",
            "3150": "3F",
            "35": "YA"
        }

        thicknessCode = {
            "0.22" : 2,
            "0.33" : 3,
            "0.44" : 4,
            "0.55" : 5,
            "0.5": 5,
            "0.9": 8
        }

        temperatureCode = {
            "SL" : "1X",
            "CH" : "2C",
            "CJ" : "3C",
            "UJ" : "3U",
            "CK" : "4C",
            "C0G" : "5C",
            "U2J" : "7U"
        }

        with open(inFile, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            reader.next() # Skip a line
            packages = reader.next()[1:]
            thickness = reader.next()[1:]
            voltage = reader.next()[1:]
            reader.next() # Skip a line
            for row in reader:
                value = row[0]
                capacity = value.replace("pF","")
                capVal = float(capacity)
                if capVal < 10.0:
                    values = map(lambda x : float(x) / 10.0, range(int(capVal*10),int(capVal*10)+9,1))
                else:
                    values = [capVal]
                for v in values:
                    valueCode, valueText = makeValueCodeAndText(v)
                    for temparature,pkg,thick, WVDC in zip(row[1:],packages,thickness,voltage):
                        if temparature != "":
                            pkg = "{:0>4}".format(mmToInchPkgMap[pkg])
                            dimension = inchPkgToCodeMap[pkg]
                            height = thicknessCode[thick]
                            alias="GRM%s%s%s%s%s"%(dimension,height,temperatureCode[temparature],voltageMap[WVDC],valueCode)
                            partId = "capacitor_{:}_{:}_chip_{:}".format(valueText,WVDC,pkg)
                            print partId
                            if not partId in self.parts:
                                self.parts[partId] = ("capacitor,%s,C,chip_capacitor_%s,Capacitor %s 5%% %sV,\"capacitor,smd\",1,2,%s,5%%,%sV"%(partId.replace(" ","_"),pkg,valueText,WVDC,valueText,WVDC),[alias])
                            else:
                                self.parts[partId][1].append(alias)

    def WriteResult(self,outFile):
        for k,v in self.parts.iteritems():
            outFile.write(v[0])
            outFile.write(",\"")
            outFile.write(",".join(v[1]))
            outFile.write("\"\n")


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--murata', nargs='+', metavar='murata', type=str,
            help='list of csv files containing pin lists producing capacitor symbols')
    parser.add_argument('--avx', nargs='+', metavar='avx', type=str,
            help='list of csv files containing pin lists producing capacitor symbols')
    parser.add_argument('--output', metavar='out', type=str,
            help='the flat condensator table file', required=True)
    args = parser.parse_args()
    output = open(args.output, "w")
    # write the header
    output.write("symbol,name,reference,footprint,description,keywords,1,2,value,tolerance,voltage\n")
    generator = CapacitorTableGenerator()
    if args.murata != None:
        for src in args.murata:
            generator.MakeMurataGRMSerieSet(src)

    if args.avx != None:
        for src in args.avx:
            generator.MakeAVXCondensatorSet(src)

    generator.WriteResult(output)
