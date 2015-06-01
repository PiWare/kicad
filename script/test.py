#!/usr/bin/python

import re
import csv
import StringIO
import symbol

#file = open("data/template/resistor.lib", "r")
file = open("data/template/test.lib", "r")
sym = StringIO.StringIO(re.sub('^#.*$\s*', '', file.read(), 0, re.M))
file.close()

inDef = False
inDraw = False
for row in csv.reader(sym, delimiter = " ", skipinitialspace = True):
    print row
    if row[0] == 'DEF':
        inDef = True
    elif row[0] == 'DRAW':
        inDraw = True
    elif row[0] == 'ENDDEF':
        inDef = False
    elif row[0] == 'ENDDRAW':
        inDraw = False

    if inDraw:
        for i in range(len(row)):
           try:
               row[i] = int(row[i])
           except:
               pass

        type = row[0]
        row.pop(0)
        if type == 'S':
            data = dict(zip(['x1', 'y1', 'x2', 'y2', 'unit', 'convert', 'lineWidth', 'fill'], row))
            print data
            r = symbol.Rectangle(**data)
            print r.render()

        elif type == 'P':
            data = dict(zip(['unit', 'convert', 'width', 'fill'], row[1:4]+row[-1:]))
            p = symbol.Polygon(**data)
            print data
            print row[4:-1]

        elif type == 'X':
            data = dict(zip(['name', 'number', 'x', 'y', 'length', 'orientation', 'numberTextSize', 'nameTextSize', 'unit', 'convert', 'type', 'shape'], row))

        elif type == 'T':
            data = dict(zip(['orientation', 'x', 'y', 'size', 'unit', 'convert', 'text'], row))
        #   symbol.Text(**data)

        elif type == 'X':
            data = dict(zip(['name', 'number', 'x', 'y', 'length', 'orientation', 'numberTextSize', 'nameTextSize', 'unit', 'convert', 'type', 'shape'], row))
            print data
