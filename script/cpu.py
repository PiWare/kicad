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

#     This script is used to generate a kicad symbol for a cpu type module.
#     The script expect a csv with the following format (which is the format provided by TI for some parts):
#       Part, "Part name"
#       Package, Package name
#       Number,Name,Type,Buffer,Description
#       "1","PB6","I/O","TTL","GPIO port B bit 6.",
#       ...
#
#     The column type can contain:
#      - I for input
#      - O for output
#      - I/O for input / output
#      - N for not connected
#      - - or S for power supply pins
#
#     The script allows pins to appear multiple times, each line documenting a
#     specific function of the pin. The script tries to group the pins by 8 or by port.
#     The supply pins are put in a seperate block



import csv
import re
import string
from string import split
import itertools

import config
from symbol import *

csvPinTypeToPinType = {
        "I" : "I",
        "O" : "O",
        "I/O" : "B",
        "N" : "N",
        "-" : "W",
        "S" : "W"
        }

class Square(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def getRep(self, pins, symbolNameWidth, grp, nameCentered):
        maxPinNameWidth = 0
        if len(pins["L"])>0:
            maxPinNameWidth = max(maxPinNameWidth, max(x.length for x in pins["L"]))+cfg.SYMBOL_PIN_TEXT_OFFSET
        if len(pins["R"])>0:
            maxPinNameWidth = max(maxPinNameWidth, max(x.length for x in pins["R"]))+cfg.SYMBOL_PIN_TEXT_OFFSET

        maxPinNameHeight = 0
        if len(pins["U"])>0:
            maxPinNameHeight = max(maxPinNameHeight, max(x.length for x in pins["U"]))+cfg.SYMBOL_PIN_TEXT_OFFSET
        if len(pins["D"])>0:
            maxPinNameHeight = max(maxPinNameHeight, max(x.length for x in pins["D"]))+cfg.SYMBOL_PIN_TEXT_OFFSET
        maxPinsHoriz = max(len(pins["U"]), len(pins["D"]))
        maxPinsVert = max(len(pins["R"]), len(pins["L"]))

        width = max([symbolNameWidth, maxPinNameWidth, maxPinsHoriz*cfg.SYMBOL_GRID*3])
        height = max(maxPinNameHeight, maxPinsVert*cfg.SYMBOL_GRID*3)+cfg.SYMBOL_TEXT_MARGIN
        if len(pins["U"]) > 0 and len(pins["D"])>0:
            height = height + cfg.SYMBOL_TEXT_MARGIN

        if len(pins["R"]) > 0 and len(pins["L"])>0:
            width = width + cfg.SYMBOL_TEXT_MARGIN

        if nameCentered == True:
            x = self.x-width/2
            y = self.y-height/2
        else:
            x = self.x
            y = self.y

        return "S %i %i %i %i %i 1 %i N"%(x, y, x+width, y+height, grp, cfg.SYMBOL_LINE_WIDTH), [x,y,x+width,y+height]

class Module(object):
    PinOffset = {
            "U" : (0,-cfg.SYMBOL_PIN_LENGTH),
            "D" : (0,cfg.SYMBOL_PIN_LENGTH),
            "L" : (cfg.SYMBOL_PIN_LENGTH,0),
            "R" : (-cfg.SYMBOL_PIN_LENGTH,0)
            }
    PinStep = {
            "U" : (cfg.SYMBOL_GRID*3,0),
            "D" : (cfg.SYMBOL_GRID*3,0),
            "L" : (0,cfg.SYMBOL_GRID*3),
            "R" : (0,cfg.SYMBOL_GRID*3)
            }

    PinStartOffset = {
            "U" : (cfg.SYMBOL_GRID*3,0),
            "D" : (cfg.SYMBOL_GRID*3,0),
            "L" : (0,cfg.SYMBOL_GRID),
            "R" : (0,cfg.SYMBOL_GRID)
            }



    def __init__(self, representation, number):
        self.representation = representation
        self.number = number
        self.pins = { "U" : [], "L" : [], "R" : [], "D" : [] }

    def addPin(self, pin, orientation):
        self.pins[orientation].append(pin)

    def getPinRepList(self, orientation, xStart, yStart):
        if self.number != 0:
            convert = 1
        else:
            convert = 0
        pinStep = Module.PinStep[orientation]
        pinOffset = Module.PinOffset[orientation]
        startOffset = Module.PinStartOffset[orientation]
        pinRange = range(0,len(self.pins[orientation]))
        return [self.pins[orientation][x].getRep(xStart+startOffset[0]+x*pinStep[0]+pinOffset[0], yStart+startOffset[1]+x*pinStep[1]+pinOffset[1], orientation, self.number, convert) for x in pinRange]

    def getRep(self, symbolName, symbolNameXPos, nameCentered):
        symbolRep, symbolOutline = self.representation.getRep(self.pins, symbolNameXPos+len(symbolName)*cfg.SYMBOL_NAME_SIZE/2, self.number, nameCentered)
        return ([symbolRep]
                + self.getPinRepList("U",symbolOutline[0],symbolOutline[1])
                + self.getPinRepList("D",symbolOutline[0],symbolOutline[3])
                + self.getPinRepList("L",symbolOutline[2],symbolOutline[1])
                + self.getPinRepList("R",symbolOutline[0],symbolOutline[1]))

def ReadHeader(reader):
    result = {}
    for row in reader:
        if len(row)>0:
            if row[0] != 'Number':
                result[row[0]]=row[1]
            else:
                return result;

def MakeMultiSymbol(inFile, outFile):
    """ Output a new part in the outFile library.
        The part will contain multiple modules grouping pins by ports.
    """
    startPins = False
    partName = ""
    pins = {}
    portGroups = {}
    gndGrp = []
    vddGrp = []
    catchName = re.compile('\A[a-zA-Z]+')
    findGnd = re.compile('(GND)|(VSS)')
    with open(inFile, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        header = ReadHeader(reader)
        for row in reader:
            if len(row) > 0:
                pinNum = int(row[0])
                if pinNum in pins:
                    pins[pinNum][1].append(row[1])
                else:
                    pins[pinNum] = (csvPinTypeToPinType[row[2]],split(row[1],'/'))
                    if pins[pinNum][0] == 'W':
                        if findGnd.match(row[1]):
                            gndGrp.append(pinNum)
                        else:
                            vddGrp.append(pinNum)
                    else:
                        portGroupName = catchName.search(row[1]).group(0)
                        if portGroupName in portGroups:
                            portGroups[portGroupName].append(pinNum)
                        else:
                            portGroups[portGroupName] = [pinNum]
    fullPortGrps = {}
    for grpName, grpPins in portGroups.iteritems():
        if len(grpPins) >= 8:
            fullPortGrps[grpName]=grpPins
    for grpName, grpPins in fullPortGrps.iteritems():
        del portGroups[grpName]
    while len(portGroups) > 0:
        currentGrp = []
        for grpName, grpPins in portGroups.iteritems():
            if len(currentGrp) + len(grpPins) >= 8:
                currentGrp = currentGrp + grpPins
                fullPortGrps[grpName] = currentGrp
                currentGrp = []
            else:
                currentGrp = currentGrp + grpPins
        del portGroups[grpName]
    symbol = Symbol(header,"IC",False)
    # First take care of the power module
    powerModule = symbol.addModule(Module(Square(0,0),1))
    map(lambda pin : powerModule.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"D"),vddGrp)
    map(lambda pin : powerModule.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"U"),gndGrp)
    grpIdx =2
    for grpName, grpPins in fullPortGrps.iteritems():
        newModule = symbol.addModule(Module(Square(0,0),grpIdx))
        grpIdx = grpIdx + 1
        map(lambda pin : newModule.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"R"),grpPins)


    outFile.write( string.join(symbol.getRep(),"\n" ) )
    outFile.write( "\n" )


def MakeSingleSymbol(inFile, outFile):
    """ Output a new part in the outFile library.
        The part will contain a single symbol.
    """
    startPins = False
    partName = ""
    pins = {}
    pinGrps = {
            "O" : [],
            "B" : [],
            "I" : [],
            "N" : [],
            "W" : [],
            }
    catchName = re.compile('\A[a-zA-Z]+')
    with open(inFile, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        header = ReadHeader(reader)
        for row in reader:
            if len(row) > 0:
               pinNum = int(row[0])
               if pinNum in pins:
                   pins[pinNum][1].append(row[1])
               else:
                   pinType = csvPinTypeToPinType[row[2]]
                   pins[pinNum] = (pinType,split(row[1],'/'))
                   if pinType == 'W':
                       if row[1][0] == 'G': # GND pins
                           pinType = "GND"
                       elif row[1][0] == 'V':
                           pinType = "VDD"
                   if pinType in pinGrps:
                       pinGrps[pinType].append(pinNum)
                   else:
                       pinGrps[pinType]=[pinNum]

        # seperate the power pins
    gndGrp = pinGrps["GND"]
    del pinGrps["GND"]
    vddGrp = pinGrps["VDD"]
    del pinGrps["VDD"]
    # Make the input group
    inGrp = pinGrps["I"] + pinGrps["B"]
    outGrp = pinGrps["O"]

    symbol = Symbol(header,"IC",False)
    # First take care of the power module
    module = symbol.addModule(Module(Square(0,0),1))
    map(lambda pin : module.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"D"),vddGrp)
    map(lambda pin : module.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"U"),gndGrp)
    map(lambda pin : module.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"R"),inGrp)
    map(lambda pin : module.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"L"),outGrp)

    outFile.write( string.join(symbol.getRep(),"\n" ) )
    outFile.write( "\n" )

def MakeRoundClockSymbol(inFile, outFile):
    """ Output a new part in the outFile library.
        The part will contain a single symbol with the pins
        layed out clockwise according to the pin numer.
    """
    startPins = False
    partName = ""
    pins = {}
    catchName = re.compile('\A[a-zA-Z]+')
    with open(inFile, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        header = ReadHeader(reader)
        for row in reader:
            if len(row) > 0:
                pinNum = int(row[0])
                if pinNum in pins:
                    pins[pinNum][1].append(row[1])
                else:
                    pinType = csvPinTypeToPinType[row[2]]
                    pins[pinNum] = (pinType,split(row[1]))

    nbPins = len(pins)
    grp1 = range(nbPins/4-1,-1,-1)
    grp2 = range(nbPins/4,nbPins/2)
    grp3 = range(nbPins/2,nbPins*3/4,1)
    grp4 = range(nbPins-1,nbPins*3/4-1,-1)
    symbol = Symbol(header,"IC",True)
    # First take care of the power module
    module = symbol.addModule(Module(Square(0,0),1))
    map(lambda pin : module.addPin(Pin(pins[pin+1][1][0],pin,pins[pin+1][0]),"R"),grp1)
    map(lambda pin : module.addPin(Pin(pins[pin+1][1][0],pin,pins[pin+1][0]),"U"),grp2)
    map(lambda pin : module.addPin(Pin(pins[pin+1][1][0],pin,pins[pin+1][0]),"L"),grp3)
    map(lambda pin : module.addPin(Pin(pins[pin+1][1][0],pin,pins[pin+1][0]),"D"),grp4)

    outFile.write( string.join(symbol.getRep(),"\n" ) )
    outFile.write( "\n" )



if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--grouped', nargs='+', metavar='grouped', type=str,
            help='list of csv files containing pin lists producing symbols with multiple groups')
    parser.add_argument('--single', nargs='+', metavar='single', type=str,
            help='list of csv files containing pin lists producing a single symbol')
    parser.add_argument('--clock', nargs='+', metavar='clock', type=str,
            help='list of csv files containing pin lists producing a single clock wise organized symbol')
    parser.add_argument('--output', metavar='out', type=str,
            help='the kicad library output file', required=True)
    args = parser.parse_args()
    output = open(args.output, "w")
    output.write("EESchema-LIBRARY Version 2.3\n")


    if args.grouped != None:
        for src in args.grouped:
            MakeMultiSymbol(src, output)
    if args.single != None:
        for src in args.single:
            MakeSingleSymbol(src, output)
    if args.clock != None:
        for src in args.clock:
            MakeRoundClockSymbol(src, output)
