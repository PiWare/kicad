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

from symbol import Symbol, Pin, cfg

# Dictionary to convert the csv pin type encoding to the kicad encoding.
csvPinTypeToPinType = {
        "I" : "I",
        "O" : "O",
        "I/O" : "B",
        "N" : "N",
        "-" : "W",
        "S" : "W",
        "GND" : "W",
        "VDD" : "W"
        }

class Square(object):
    """Schematic square object representation."""
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def render(self, pins, symbolNameWidth, grp):
        """Build a graphical representation able to contain all the pin names provided in the pins list.
        Returns a tuple containing the representation of the square symbol followed by the computed bounderies.
        """

        # Determine the square width
        maxPinNameWidth = 0
        if len(pins["L"])>0:
            maxPinNameWidth = max(maxPinNameWidth, max(x.length for x in pins["L"]))+cfg.SYMBOL_PIN_TEXT_OFFSET
        if len(pins["R"])>0:
            maxPinNameWidth = max(maxPinNameWidth, max(x.length for x in pins["R"]))+cfg.SYMBOL_PIN_TEXT_OFFSET

        # determine the square height
        maxPinNameHeight = 0
        if len(pins["U"])>0:
            maxPinNameHeight = max(maxPinNameHeight, max(x.length for x in pins["U"]))+cfg.SYMBOL_PIN_TEXT_OFFSET
        if len(pins["D"])>0:
            maxPinNameHeight = max(maxPinNameHeight, max(x.length for x in pins["D"]))+cfg.SYMBOL_PIN_TEXT_OFFSET
        maxPinsHoriz = max(len(pins["U"]), len(pins["D"]))
        maxPinsVert = max(len(pins["R"]), len(pins["L"]))

        width = max([symbolNameWidth, maxPinNameWidth, maxPinsHoriz*cfg.SYMBOL_PIN_GRID*3])
        height = max(maxPinNameHeight, maxPinsVert*cfg.SYMBOL_PIN_GRID*3)+cfg.SYMBOL_PIN_TEXT_OFFSET

        # Add a bit of space between the pins and the border of the outline
        if len(pins["U"]) > 0 and len(pins["D"])>0:
            height = height + cfg.SYMBOL_PIN_TEXT_OFFSET

        if len(pins["R"]) > 0 and len(pins["L"])>0:
            width = width + cfg.SYMBOL_PIN_TEXT_OFFSET

        #if nameCentered == True:
        x = self.x-width/2
        y = self.y-height/2
        #else:
        #   x = self.x
        #   y = self.y

        return "S %i %i %i %i %i 1 %i N"%(x, y, x+width, y+height, grp, cfg.SYMBOL_LINE_WIDTH), [x,y,x+width,y+height]

class Pin(object):
    FormatString = "X %s %i %i %i " + str(cfg.SYMBOL_PIN_LENGTH) + " %s " + str(cfg.SYMBOL_PIN_NUMBER_SIZE) + " " + str(cfg.SYMBOL_PIN_NAME_SIZE) + " %i %i %s"

    def __init__(self, name, number, type):
        self.name = name
        self.length = len(name)*cfg.SYMBOL_PIN_NAME_SIZE
        self.type = type
        self.number = number
    
    def getRep(self,x,y,orientation,group,convert):
        return Pin.FormatString %(self.name, self.number, x, y, orientation, group, convert, self.type)

class Module(object):
    """Represents a kicad schematic module instance."""
    PinOffset = {
            "U" : (0,-cfg.SYMBOL_PIN_LENGTH),
            "D" : (0,cfg.SYMBOL_PIN_LENGTH),
            "L" : (cfg.SYMBOL_PIN_LENGTH,0),
            "R" : (-cfg.SYMBOL_PIN_LENGTH,0)
            }
    PinStep = {
            "U" : (cfg.SYMBOL_PIN_GRID*3,0),
            "D" : (cfg.SYMBOL_PIN_GRID*3,0),
            "L" : (0,cfg.SYMBOL_PIN_GRID*3),
            "R" : (0,cfg.SYMBOL_PIN_GRID*3)
            }

    PinStartOffset = {
            "U" : (cfg.SYMBOL_PIN_GRID*3,0),
            "D" : (cfg.SYMBOL_PIN_GRID*3,0),
            "L" : (0,cfg.SYMBOL_PIN_GRID),
            "R" : (0,cfg.SYMBOL_PIN_GRID)
            }



    def __init__(self, representation, number):
        """Create a new instance of a module.

        representation -- object modeling the schematic representation of the module.
        number -- module number
        """
        self.representation = representation
        self.number = number
        self.pins = { "U" : [], "L" : [], "R" : [], "D" : [] }
        self.unit = 0

    def addPin(self, pin, orientation):
        """Add a pin to the module with the given orientation."""
        self.pins[orientation].append(pin)

    def getPinRepList(self, orientation, xStart, yStart):
        """Build the pin representation for the module. Laying out the pins around the symbol representation."""
        if self.number != 0:
            convert = 1
        else:
            convert = 0
        pinStep = Module.PinStep[orientation]
        pinOffset = Module.PinOffset[orientation]
        startOffset = Module.PinStartOffset[orientation]
        pinRange = range(0,len(self.pins[orientation]))
        return [self.pins[orientation][x].render(xStart+startOffset[0]+x*pinStep[0]+pinOffset[0], yStart+startOffset[1]+x*pinStep[1]+pinOffset[1], orientation, self.number, convert) for x in pinRange]

    def render(self, symbolName, symbolNameXPos):
        """Build the module representation including all the pins the name and the symbol reference."""
        symbolRep, symbolOutline = self.representation.render(self.pins, symbolNameXPos+len(symbolName)*cfg.SYMBOL_NAME_SIZE/2, self.number)
        return ([symbolRep]
                + self.getPinRepList("U",symbolOutline[0],symbolOutline[1])
                + self.getPinRepList("D",symbolOutline[0],symbolOutline[3])
                + self.getPinRepList("L",symbolOutline[2],symbolOutline[1])
                + self.getPinRepList("R",symbolOutline[0],symbolOutline[1]))

class Symbol(object):
    DefFormat="DEF %s %s 0 "+str(cfg.SYMBOL_PIN_TEXT_OFFSET)+" Y Y %i L N"
    RefFieldFormat = ( "F%i"%(cfg.REFERENCE_FIELD)
            + ' "%s" %i %i'
            + " " + str(cfg.SYMBOL_NAME_SIZE)
            + " H V C CNN")

class Cpu(Symbol):
    def __init__(self, name, ref, nameCentered, package = ""):
        super(Cpu,self).__init__(name, ref, package)
        self.nameCentered = nameCentered

    def refFieldPos(self):
        if self.nameCentered:
            return ( -(len(self.reference)+4)/4*cfg.SYMBOL_NAME_SIZE
                    , -cfg.SYMBOL_PIN_TEXT_OFFSET )
        else:
            return ( cfg.SYMBOL_PIN_TEXT_OFFSET, cfg.SYMBOL_NAME_SIZE )

    def valueFieldPos(self):
        if self.nameCentered:
            return ( -(len(self.name))/4*cfg.SYMBOL_NAME_SIZE
                    , cfg.SYMBOL_PIN_TEXT_OFFSET )
        else:
            return ( (len(self.name)/2 + len(self.reference)+4)*cfg.SYMBOL_NAME_SIZE+cfg.SYMBOL_PIN_TEXT_OFFSET,
                cfg.SYMBOL_NAME_SIZE
            )


def ReadHeader(reader):
    """Read the header lines from the csv reader."""

    result = {}
    for row in reader:
        if len(row)>0:
            # The end of the header is marked by "Number" in the first column.
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
    # Open the chip input file
    with open(inFile, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        # read the header of the symbol data
        header = ReadHeader(reader)
        # read the pin names, types and descriptions.
        for row in reader:
            if len(row) > 0:
                pinNum = int(row[0])
                if pinNum in pins:
                    pins[pinNum][1].append(row[1])
                else:
                    pins[pinNum] = (csvPinTypeToPinType[row[2]],split(row[1],'/'))
                    # for ground and power source pins, put them in a special list
                    if pins[pinNum][0] == 'W':
                        if findGnd.match(row[1]):
                            gndGrp.append(pinNum)
                        else:
                            vddGrp.append(pinNum)
                    else:
                        # build the pin grouping dictionary
                        portGroupName = catchName.search(row[1]).group(0)
                        if portGroupName in portGroups:
                            portGroups[portGroupName].append(pinNum)
                        else:
                            portGroups[portGroupName] = [pinNum]
    # Filter out the port groups containing at least 8 pins
    fullPortGrps = {}
    for grpName, grpPins in portGroups.iteritems():
        if len(grpPins) >= 8:
            fullPortGrps[grpName]=grpPins
    # Remove all the port groups from the group dictionary
    for grpName, grpPins in fullPortGrps.iteritems():
        del portGroups[grpName]

    # build port groups by concatenating incomplete groups together
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
    # Create the symbol for the chip
    symbol = Cpu(header["Part"],"IC",False,header["Package"])
    # First take care of the power module
    powerModule = symbol.addModule(Module(Square(0,0),1))
    map(lambda pin : powerModule.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"D"),vddGrp)
    map(lambda pin : powerModule.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"U"),gndGrp)
    # Add the positioningrt groups and modules
    grpIdx =2
    for grpName, grpPins in fullPortGrps.iteritems():
        newModule = symbol.addModule(Module(Square(0,0),grpIdx))
        grpIdx = grpIdx + 1
        map(lambda pin : newModule.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"R"),grpPins)


    # write out the symbol to the output file. The list of strings needs to be assembled through a string join to add new line characters.
    outFile.write( string.join(symbol.render(),"\n" ) )
    outFile.write( "\n" )


def MakeSingleSymbol(inFile, outFile):
    """ Output a new part in the outFile library.
        The part will contain a single module.
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
    inPinNames = [string.join(pins[x][1],'/') for x in inGrp]
    inGrpTextLength = max([len(x) for x in inPinNames]+[1])*40
    outGrp = pinGrps["O"]
    outPinNames = [string.join(pins[x][1],'/') for x in outGrp]
    outGrpTextLength = max([len(x) for x in outPinNames]+[1])*40
    minWidth = len(partName)*60+250+40
    # Evaluate the size of the symbol
    height = max(len(inGrp),len(outGrp))*120+350+40+240 # +240 for the supply pins 
    width = max(minWidth,max([len(gndGrp)*120, len(vddGrp)*120, outGrpTextLength, inGrpTextLength])+200)
    # Output the part header
    outFile.write( "DEF %s IC 0 40 Y Y 1 L N\n"%(partName) )
    outFile.write( 'F0 "IC" 150 270 60 H V C CNN\n')
    outFile.write( 'F1 "%s" %i %i 60 H V C CNN\n'%(partName, len(partName)*60/2+250,270) )
    outFile.write( "DRAW\n" )

    symbol = Cpu(header["Part"],"IC",False,header["Package"])
    # First take care of the power module
    module = symbol.addModule(Module(Square(0,0),1))
    map(lambda pin : module.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"D"),vddGrp)
    map(lambda pin : module.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"U"),gndGrp)
    map(lambda pin : module.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"R"),inGrp)
    map(lambda pin : module.addPin(Pin(string.join(pins[pin][1],'/'),pin,pins[pin][0]),"L"),outGrp)

    outFile.write( string.join(symbol.render(),"\n" ) )
    outFile.write( "\n" )

def MakeRoundClockSymbol(inFile, outFile):
    """ Output a new part in the outFile library.
        The part will contain a single symbol with the pins
        layed out clockwise according to the pin number.
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
    symbol = Cpu(header["Part"],"IC",True,header["Package"])
    # First take care of the power module
    module = symbol.addModule(Module(Square(0,0),1))
    map(lambda pin : module.addPin(Pin(pins[pin+1][1][0],pin,pins[pin+1][0]),"R"),grp1)
    map(lambda pin : module.addPin(Pin(pins[pin+1][1][0],pin,pins[pin+1][0]),"U"),grp2)
    map(lambda pin : module.addPin(Pin(pins[pin+1][1][0],pin,pins[pin+1][0]),"L"),grp3)
    map(lambda pin : module.addPin(Pin(pins[pin+1][1][0],pin,pins[pin+1][0]),"D"),grp4)

    outFile.write( string.join(symbol.render(),"\n" ) )
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

    # Process the data files according to the method selected by the command line arguments.
    if args.grouped != None:
        for src in args.grouped:
            MakeMultiSymbol(src, output)
    if args.single != None:
        for src in args.single:
            MakeSingleSymbol(src, output)
    if args.clock != None:
        for src in args.clock:
            MakeRoundClockSymbol(src, output)
