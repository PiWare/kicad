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

#     This script is used to generate a kicad symbol for a range of resistors.
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

class Resistor(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def render(self, pins, symbolNameWidth, grp, nameCentered):
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

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--family', nargs='+', metavar='family', type=str,
            help='list of csv files containing pin lists producing symbols with multiple groups')
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
