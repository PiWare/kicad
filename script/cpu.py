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

csvPinTypeToPinType = {
    "I" : "I",
    "O" : "O",
    "I/O" : "B",
    "N" : "N",
    "-" : "W",
    "S" : "W"
}

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
        for row in reader:
            if len(row) > 0:
                if startPins:
                    pinNum = int(row[0])
                    if pinNum in pins:
                        pins[pinNum][1].append(row[1])
                    else:
                        pins[pinNum] = (csvPinTypeToPinType[row[2]],[row[1]])
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
                else:
                    if row[0] == 'Part':
                        partName=row[1]
                    elif row[0] == 'Number':
                        startPins = True
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
    
    # Output the part header
    outFile.write( "DEF %s IC 0 40 Y Y %i L N\n"%(partName, len(fullPortGrps)+1))
    outFile.write( 'F0 "IC" 150 150 60 H V C CNN\n' )
    outFile.write( 'F1  "%s" %i %i 60 H V C CNN\n'%(partName, len(partName)*60/2+250,150))
    minWidth = len(partName)*60+250+40
    outFile.write( "DRAW\n" )
    # First take care of the power supply pins
    width = max(minWidth, max(len(gndGrp),len(vddGrp))*120+200)
    outFile.write( "S 0 50 %i %i 1 1 1 N\n"%( width, 9*150+70))
    for index in range(0,len(vddGrp)):
        pin = vddGrp[index]
        outFile.write( "X %s %i %i %i 200 U 40 40 1 0 %s\n"%(string.join(pins[pin][1],'/'), pin, 100+index*120, 9*150+70, pins[pin][0] ))
    for index in range(0,len(gndGrp)):
        pin = gndGrp[index]
        outFile.write( "X %s %i %i 50 200 D 40 40 1 0 %s\n"%(string.join(pins[pin][1],'/'), pin, 100+index*120, pins[pin][0] ))
    # Output the I/O pins to their attributed modules
    grpIdx = 2
    for grpName, grpPins in fullPortGrps.iteritems():
        nbPins = len(grpPins)
        pinNames = [string.join(pins[x][1],'/') for x in grpPins] 
        maxTextLength = max([len(x) for x in pinNames])
        # Evaluate the size of the symbol
        height = nbPins*120+350+40
        width = max(minWidth,maxTextLength*40+200)
        outFile.write( "S 0 50 %i %i %i 1 1 N\n"%(width, height, grpIdx))
        for index in range(0,nbPins):
            pin = grpPins[index]
            outFile.write( "X %s %i -200 %i 200 R 40 40 %i 1 %s\n"%( pinNames[index], pin, 350+index*120, grpIdx, pins[pin][0] ))
        grpIdx = grpIdx + 1
    # Symbol end
    outFile.write( "ENDDRAW\n" )
    outFile.write( "ENDDEF\n" )


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
        for row in reader:
            if len(row) > 0:
                if startPins:
                    pinNum = int(row[0])
                    if pinNum in pins:
                        pins[pinNum][1].append(row[1])
                    else:
                        pinType = csvPinTypeToPinType[row[2]]
                        pins[pinNum] = (pinType,[row[1]])
                        if pinType == 'W':
                            if row[1][0] == 'G': # GND pins
                                pinType = "GND"
                            elif row[1][0] == 'V':
                                pinType = "VDD"
                        if pinType in pinGrps:
                            pinGrps[pinType].append(pinNum)
                        else:
                            pinGrps[pinType]=[pinNum]
                else:
                    if row[0] == 'Part':
                        partName=row[1]
                    elif row[0] == 'Number':
                        startPins = True
    
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

    outFile.write( "S 0 50 %i %i 1 1 1 N\n"%( width, height ) )
    # First take care of the power supply pins
    for index in range(0,len(vddGrp)):
        pin = vddGrp[index]
        outFile.write( "X %s %i %i %i 200 D 40 40 1 1 %s\n"%(string.join(pins[pin][1],'/'), pin, 100+index*120, height+200, pins[pin][0]) )
    for index in range(0,len(gndGrp)):
        pin = gndGrp[index]
        outFile.write( "X %s %i %i -150 200 U 40 40 1 1 %s\n"%(string.join(pins[pin][1],'/'), pin, 100+index*120, pins[pin][0]) )
    # Output the output pins 
    for index in range(0,len(outGrp)):
        pin = outGrp[index]
        outFile.write( "X %s %i %i %i 200 L 40 40 1 1 %s\n"%(outPinNames[index], pin, width+200, 470+index*120, pins[pin][0]) )

    # Output the input pins 
    for index in range(0,len(inGrp)):
        pin = inGrp[index]
        outFile.write( "X %s %i -200 %i 200 R 40 40 1 1 %s\n"%( inPinNames[index], pin, 470+index*120, pins[pin][0]) )
   
    # Symbol end
    outFile.write( "ENDDRAW\n" )
    outFile.write( "ENDDEF\n" )



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--grouped', nargs='+', metavar='grouped', type=str,
                       help='list of csv files containing pin lists producing symbols with multiple groups')
    parser.add_argument('--single', nargs='+', metavar='single', type=str,
                       help='list of csv files containing pin lists producing a single symbol')
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
