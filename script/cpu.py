#!/usr/bin/python

import csv
import re
import string

csvPinTypeToPinType = {
    "I" : "I",
    "O" : "O",
    "I/O" : "B",
    "-" : "W"
}

def MakeSymbol(infile, outfile):
    startPins = False
    partName = ""
    pins = {}
    portGroups = {}
    gndGrp = []
    vddGrp = []
    catchName = re.compile('\A[a-zA-Z]+')
    with open(infile, 'rb') as csvfile:
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
                            if row[1][0] == 'G':
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
    print fullPortGrps
    print portGroups
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
    print "DEF ", partName, "IC 0 40 Y Y %i L N"%(len(fullPortGrps))
    print 'F0 "IC" 150 150 60 H V C CNN'
    print "F1", '"%s"'%(partName), len(partName)*60/2+150,9*150,"60 H V C CNN"
    print "DRAW"
    print "S 0 50", max(len(gndGrp),len(vddGrp))*120+200, 9*150+70, "1 1 1 N"
    for index in range(0,len(vddGrp)):
        pin = vddGrp[index]
        print "X", string.join(pins[pin][1],'/'), pin, 100+index*120, 9*150+70,"200 U 40 40 1 0", pins[pin][0]
    for index in range(0,len(gndGrp)):
        pin = gndGrp[index]
        print "X", string.join(pins[pin][1],'/'), pin, 100+index*120, "50 200 D 40 40 1 0", pins[pin][0]
    grpIdx = 2
    for grpName, grpPins in fullPortGrps.iteritems():
        nbPins = len(grpPins)
        pinNames = [string.join(pins[x][1],'/') for x in grpPins] 
        maxTextLength = max([len(x) for x in pinNames])
        print "S 0 50", maxTextLength*40+200, 9*150+70, grpIdx,"1 1 N"
        for index in range(0,nbPins):
            pin = grpPins[index]
            print "X", pinNames[index], pin, "-200",350+index*120,"200 R 40 40",grpIdx,"1", pins[pin][0]
        grpIdx = grpIdx + 1
    print "ENDDRAW" 
    print "ENDDEF" 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('pins', metavar='csv', type=str,
                       help='the csv file containing the pin list for the symbol')
    parser.add_argument('output', metavar='out', type=str,
                       help='the output file containing the symbol')
    args = parser.parse_args()
    print "EESchema-LIBRARY Version 2.3"
    MakeSymbol(args.pins, args.output)
