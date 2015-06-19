#!/usr/bin/python

# http://www.nxp.com/technical-support-portal/#/tid=50808,tab=datasheets

import os
import sys
import symbol
from symbol import cfg
import csv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Symbol generator from csv table.')
    parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
#   parser.add_argument('--symbol', metavar = 'symbol', type = str, help = 'Output file for generated KiCAD symbols', required = True)
#   parser.add_argument('--desc', metavar = 'desc', type = str, help = 'Output file for generated KiCAD symbol description', required = True)
#   parser.add_argument('--template_path', metavar = 'template_path', type = str, help = 'Path to template symbols', required = True)
    args = parser.parse_args()

#   symbol_output = open(args.symbol, "w")
#   symbol_output.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
#   desc_output = open(args.desc, "w")
#   desc_output.write('EESchema-DOCLIB Version 2.0\n')

    pinGrid = 200
    pinSpace = 200
    pinLength = 200
    fontSize = 50
    lineWidth = 20
    referenceSpace = 500

    sym = symbol.Symbol()
    left = []
    right = []
    up = []
    down = []
    with open(args.csv, 'rb') as csvfile:
        table = csv.reader(csvfile, delimiter=',', quotechar='\"')

        first_row = 1
        for row in table:
            if first_row == 1:
                header = row
                first_row = 0
            else:
                for i in range(len(row)):
                    try:
                        row[i] = int(row[i])
                    except:
                        pass
                data = dict(zip(header, row))

                direction = data['direction']
                #del data['direction']

                if direction == 'left':
                    left.append(data)
                elif direction == 'right':
                    right.append(data)
                elif direction == 'up':
                    up.append(data)
                elif direction == 'down':
                    down.append(data)

#               if not os.path.isfile(template_file):
#                   print "Template file '%s' does not exist!"%(template_file)
#                   sys.exit(2)

#                   if 'sym' in locals():
#                       sym.optimize()
#                       symbol_output.write("\n".join(sym.renderSymbol()))
#                       desc_output.write("\n".join(sym.renderDescription()))
#                       del sym
    nameWidthLeft = 0
    nameWidthRight = 0
    nameHeightUp = 0
    nameHeightDown = 0
    for data in left:
        nameWidthLeft = max(nameWidthLeft, len(data['name'].translate(None, "~")) * fontSize)
    for data in right:
        nameWidthRight = max(nameWidthRight, len(data['name'].translate(None, "~")) * fontSize)

    for data in up:
        nameHeightUp = max(nameHeightUp, len(data['name'].translate(None, "~")) * fontSize)
    for data in down:
        nameHeightDown = max(nameHeightDown, len(data['name'].translate(None, "~")) * fontSize)

    nameWidth = nameWidthLeft + referenceSpace + nameWidthRight
    nameHeight = nameHeightUp + nameHeightDown
    print nameWidth, nameHeight

    width = (max(len(up), len(down)) - 1) * pinGrid + 2 * pinSpace
    height = (max(len(left), len(right)) - 1) * pinGrid + 2 * pinSpace

    print width, height

    width = max(width, nameWidth)
    height = max(height, nameHeight)

    sym.addModule(symbol.Rectangle(-width / 2, -height / 2, width / 2, height / 2, lineWidth, symbol.fill.background, 0, symbol.representation.normal))
    sym.name = "TEST"
    sym.reference = "IC"

    x = -width / 2 - pinLength
    y = height / 2 - pinSpace
    for data in left:
        if data['type'] != 'space':
            sym.addModule(symbol.Pin_(x, y, data['name'], data['number'], pinLength, getattr(symbol.directionFlipped, data['direction']), fontSize, fontSize, 0, symbol.representation.normal,
                getattr(symbol.Type, data['type']), getattr(symbol.shape, data['shape'])))
        y -= pinGrid

    x = width / 2 + pinLength
    y = height / 2 - pinSpace
    for data in right:
        if data['type'] != 'space':
            sym.addModule(symbol.Pin_(x, y, data['name'], data['number'], pinLength, getattr(symbol.directionFlipped, data['direction']), fontSize, fontSize, 0, symbol.representation.normal,
                getattr(symbol.Type, data['type']), getattr(symbol.shape, data['shape'])))
        y -= pinGrid

    sym.optimize()
    print "\n".join(sym.renderSymbol())
#   symbol_output.write("#\n# End Library\n")
#   desc_output.write("#\n# End Doc Library\n")
