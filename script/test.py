#!/usr/bin/python

import re
import csv
import StringIO
import symbol
import itertools

#file = open("data/template/resistor.lib", "r")
file = open("data/template/test.lib", "r")
sym = StringIO.StringIO(re.sub('^#.*$\s*', '', file.read(), 0, re.M))
file.close()

inDef = False
inDraw = False
for row in csv.reader(sym, delimiter = " ", skipinitialspace = True):
#   print row
    if row[0] == 'DEF':
        inDef = True
    elif row[0] == 'DRAW':
        inDraw = True
        continue
    elif row[0] == 'ENDDEF':
        inDef = False
    elif row[0] == 'ENDDRAW':
        inDraw = False

    if inDraw:
        input = " ".join(row)
        print input
        for i in range(len(row)):
           try:
               row[i] = int(row[i])
           except:
               pass

        output = ""
        type = row[0]
        row.pop(0)
        # Polygon
        if type == 'P':
            data = dict(zip(['unit', 'representation', 'width', 'fill'], row[1:4]+row[-1:]))
            points = row[4:-1]

            poly = symbol.Polygon(**data)
            for i in range(0, len(points), 2):
                poly.add(symbol.Point(points[i], points[i + 1]))
            output = poly.render()

        # Rectangle
        elif type == 'S':
            data = dict(zip(['x1', 'y1', 'x2', 'y2', 'unit', 'representation', 'width', 'fill'], row))

            rect = symbol.Rectangle(**data)
            output = rect.render()

        # Circle
        elif type == 'C':
            data = dict(zip(['x', 'y', 'radius', 'unit', 'representation', 'width', 'fill'], row))

            circ = symbol.Circle(**data)
            output = circ.render()

        # Arc
        elif type == 'A':
            data = dict(zip(['x', 'y', 'radius', 'startAngle', 'endAngle', 'unit', 'representation', 'width', 'fill', 'startX', 'startY', 'endX', 'endY'], row))

            arc = symbol.Arc(**data)
            output = arc.render()

        # Text
        elif type == 'T':
            row.pop(4) # Pop unused argument
            data = dict(zip(['orientation', 'x', 'y', 'size', 'unit', 'representation', 'text', 'italic', 'bold', 'hjustify', 'vjustify'], row))

            text = symbol.Text(**data)
            output = text.render()

        # Pin
        elif type == 'X':
            data = dict(zip(['name', 'number', 'x', 'y', 'length', 'orientation', 'numberTextSize', 'nameTextSize', 'unit', 'representation', 'type', 'shape'], row))
            print data

        print output
        if input == output:
            print "PASS"
        else:
            print "FAILED"
        print
