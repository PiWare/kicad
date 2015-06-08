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

#     This script contains commons object definitions to generate kicad symbols

import config
import re
import csv
import StringIO
import itertools

# Load the configuration file and provide it's values through the cfg object
cfg = config.Config("config")

class fill():
    none = "N"
    foreground = "F"
    background = "f"

class representation():
    """Symbol representation"""

    both = 0
    normal = 1
    morgan = 2

class italic():
    off = "Normal"
    on = "Italic"

class bold():
    off = "0"
    on = "1"

class orientation():
    horizontal = "H"
    vertical = "V"

class visibility():
    visible = "V"
    invisible = "I"

class hjustify():
    left = "L"
    center = "C"
    right = "R"

class vjustify():
    top = "T"
    center = "C"
    bottom = "B"

class style():
    none = "NN"
    italic = "IN"
    bolc = "NB"
    italicBold = "IB"

class direction():
    up = "U"
    down = "D"
    right = "R"
    left = "L"

class Type():
    input = "I"
    output = "O"
    bidirectional = "B"
    tristate = "T"
    passive = "P"
    unspecified = "U"
    powerInput = "W"
    powerOutput = "w"
    openCollector = "C"
    openEmitter = "E"
    notConnected = "N"

# Add 'N' before characters, to create an invisible pin
class shape():
    line = ""
    invisible = "N"
    inverted = "I"
    clock = "C"
    invertedClock = "CI"
    inputLow = "L"
    clockLow = "CL"
    outputLow = "V"
    fallingEdgeClock = "F"
    nonLogic = "X"
    _inverted = "NI"
    _clock = "NC"
    _invertedClock = "NCI"
    _inputLow = "NL"
    _clockLow = "NCL"
    _outputLow = "NV"
    _fallingEdgeClock = "NF"
    _nonLogic = "NX"

class Point():
    "Represents a point"

    format = "%d %d"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, rhs):
        """ Compare only graphical elements"""
        if not isinstance(rhs, Point):
            return False

        return self.x == rhs.x and self.y == rhs.y

    def __ne__(self, rhs):
        if not isinstance(rhs, Point):
            return True

        return self.x != rhs.x or self.y != rhs.y

    def render(self):
        return Point.format%(self.x, self.y)

class Field():
    """Symbol field"""
    format = "F%d \"%s\" %d %d %d %s %s %s %s%s"

    def __init__(self, number, text, x, y, size, orientation, visibility = visibility.visible, hjustify = hjustify.center, vjustify = vjustify.center, style = style.none):
        pass

class Polygon():
    "Render polygon"
    format = "P %d %d %d %d %s%s"

    def __init__(self, width, fill = fill.background, unit = 0, representation = representation.normal):
        self.width = width
        self.fill = fill
        self.unit = unit
        self.representation = representation
        self.points = []

    def __eq__(self, rhs):
        """ Compare only graphical elements"""
        if not isinstance(rhs, Polygon):
            return False

        if len(self.points) != len(rhs.points):
            return False

        print "eq"
        for point1, point2 in zip(self.points, rhs.points):
            if point1 != point2:
                print "False"
                return False

        print "True"
        return True

    def __ne__(self, rhs):
        print "ne"

    def add(self, point):
        self.points.append(point)

    def render(self):
        pts = ""
        for point in self.points:
            pts += point.render() + " "
        return Polygon.format%(len(self.points), self.unit, self.representation, self.width, pts, self.fill)

class Rectangle():
    "Render rectangle"
    format = "S %d %d %d %d %d %d %d %s"

    def __init__(self, x1, y1, x2, y2, width, fill = fill.background, unit = 0, representation = representation.normal):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width
        self.fill = fill
        self.unit = unit
        self.representation = representation

    def __eq__(self, rhs):
        """ Compare only graphical elements"""
        if not isinstance(rhs, Rectangle):
            return False

        return self.x1 == rhs.x1 and self.y1 == rhs.y1 and self.x2 == rhs.x2 and self.y2 == rhs.y2

    def render(self):
        return Rectangle.format%(self.x1, self.y1, self.x2, self.y2, self.unit, self.representation, self.width, self.fill)

class Circle():
    "Render circle"

    format = "C %d %d %d %d %d %d %s"

    def __init__(self, x, y, radius, width, fill = fill.background, unit = 0, representation = representation.normal):
        self.x = x
        self.y = y
        self.radius = radius
        self.width = width
        self.fill = fill
        self.unit = unit
        self.representation = representation

    def __eq__(self, rhs):
        """ Compare only graphical elements"""
        if not isinstance(rhs, Circle):
            return False

        return self.x == rhs.x and self.y == rhs.y and self.radius == rhs.radius

    def render(self):
        return Circle.format%(self.x, self.y, self.radius, self.unit, self.representation, self.width, self.fill)

class Arc():
    "Render arc"

    format = "A %d %d %d %d %d %d %d %d %s %d %d %d %d"

    def __init__(self, x, y, startX, startY, endX, endY, startAngle, endAngle, radius, width, fill = fill.background, unit = 0, representation = representation.normal):
        self.x = x
        self.y = y
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.radius = radius
        self.width = width
        self.fill = fill
        self.unit = unit
        self.representation = representation

    def __eq__(self, rhs):
        """ Compare only graphical elements"""
        if not isinstance(rhs, Circle):
            return False

        return self.x == rhs.x and self.y == rhs.y and self.radius == rhs.radius

    def render(self):
        return Arc.format%(self.x, self.y, self.radius, self.startAngle, self.endAngle, self.unit, self.representation, self.width, self.fill, self.startX, self.startY, self.endX, self.endY)


class Text():
    """Format text element
        x, y - Position
        text - Text
        size - Size in mil
        orientation - Angle in centidegree (supported, but not documented!)
        unit - Unit number
        convert - Shape number
    """

    format = 'T %d %d %d %d 0 %d %d %s %s %s %s %s'

    def __init__(self, x, y, text, size, orientation = 0, unit = 0, representation = representation.normal, italic = italic.off, bold = bold.off, hjustify = hjustify.center, vjustify = vjustify.center):
        self.x = x
        self.y = y
        self.text = text.replace(' ', '~')
        self.size = size
        self.orientation = orientation
        self.unit = unit
        self.representation = representation
        self.italic = italic
        self.bold = bold
        self.hjustify = hjustify
        self.vjustify = vjustify

    def __eq__(self, rhs):
        """ Compare only graphical elements"""
        if not isinstance(rhs, Text):
            return False

        return self.x == rhs.x and self.y == rhs.y and self.text == rhs.text

    def render(self):
        return Text.format%(self.orientation, self.x, self.y, self.size, self.unit, self.representation, self.text, self.italic, self.bold, self.hjustify, self.vjustify)

class Pin_():

    format = "X %s %s %d %d %d %s %d %d %d %d %s %s"

    def __init__(self, x, y, name, number, length, orientation, nameSize, numberSize, unit = 0, representation = representation.normal, type = Type.input, shape = shape.line):
        self.x = x
        self.y = y
        self.name = name
        self.number = number
        self.length = length
        self.orientation = orientation
        self.nameSize = nameSize
        self.numberSize = numberSize
        self.unit = unit
        self.representation = representation
        self.type = type
        self.shape = shape

    def __eq__(self, rhs):
        """ Compare only graphical elements"""
        if not isinstance(rhs, Pin_):
            return False

        return False

    def render(self):
        return (Pin_.format%(self.name, self.number, self.x, self.y, self.length, self.orientation, self.numberSize, self.nameSize, self.unit, self.representation, self.type, self.shape)).rstrip()

class Pin(object):
    """Represents a pin assigned to a schematic symbol."""

    FormatString = "X %%s %%i %%i %%i %i %%s %i %i %%i %%i %%s"%(cfg.SYMBOL_PIN_LENGTH, cfg.SYMBOL_PIN_NUMBER_SIZE, cfg.SYMBOL_PIN_NAME_SIZE)

    def __init__(self, name, number, type):
        """Create a new pin object representing a symbol pin.

        name -- name of the pin
        number -- pin number
        type -- type of the pin (specified as in the kicad schematic pin type)
        """
        self.name = name
        self.length = len(name)*cfg.SYMBOL_PIN_NAME_SIZE
        self.type = type
        self.number = number

    def render(self,x,y,orientation,group,convert):
        """Make a representation for the pin using the pin properties and the positioning information.

        x -- x coordinate of the pin in the symbol representation
        y -- y coordinate of the pin in the symbol representation
        orientation -- one of 'U','D','L','R'
        group -- group number which the pin is assigned to.
        convert -- kicad convert (usually 2, or 0 for pins common to all modules)
        """
        return Pin.FormatString %(self.name, self.number, x, y, orientation, group, convert, self.type)


class Symbol(object):
    """Represents a kicad schematic library symbol."""

    DefFormat="DEF %%s %%s 0 %i Y Y %%i L N"%(cfg.SYMBOL_PIN_TEXT_OFFSET)
    RefFieldFormat = 'F%i "%%s" %%i %%i %i H V L CNN'%(cfg.REFERENCE_FIELD,cfg.SYMBOL_NAME_SIZE)
    ValueFieldFormat = 'F%i "%%s" %%i %%i %i H I L CNN'%(cfg.VALUE_FIELD,cfg.SYMBOL_NAME_SIZE)
    FootprintFieldFormat = "F%i"%(cfg.FOOTPRINT_FIELD) +' "%s" 0 0 30 H I C CCN'

    def __init__(self, name = "", ref = "", nameCentered = True, package = ""):
        """Creates a new symbol instance.

        name -- symbol name.
        ref -- kicad symbol reference string.
        nameCentered -- a boolean indicating if the name should be centered according to the symbol boundaries.
        """
        self.name = name
        self.ref = ref
        self.modules = []
        self.nameCentered = nameCentered
        self.footprint = package

    def addModule(self, module):
        """Inserts a new module to the symbol. Returns the newly added module instance."""
        self.modules.append(module)
        return module

    def refFieldPos(self):
        """Creates a pair of (x,y) coordinates specifying the position of the reference field text."""
        bounds = self.getBounds()
        return (bounds[0]+bounds[2], bounds[1]-cfg.SYMBOL_NAME_SIZE/2)

    def valueFieldPos(self):
        """Creates a pair of (x,y) coordinates specifying the position of the value field text."""
        bounds = self.getBounds()
        return (bounds[0]+bounds[2], bounds[1]+bounds[3]-cfg.SYMBOL_NAME_SIZE/2)

    def load(self, filename, unit = -1):
        """Load only graphic elements from a symbol file and add it to the given unit
            filename - Load given filename
            unit - Change loaded symbol elements to given unit. If unit = -1, no changes will be made
        """

        file = open(filename, "r")
        text = StringIO.StringIO(re.sub('^#.*$\s*', '', file.read(), 0, re.M))
        file.close()

        inDef = False
        inDraw = False
        for row in csv.reader(text, delimiter = " ", skipinitialspace = True):
            if row[0] == 'DEF':
                inDef = True
            elif row[0] == 'DRAW':
                inDraw = True
                continue
            elif row[0] == 'ENDDEF':
                inDef = False
            elif row[0] == 'ENDDRAW':
                inDraw = False

            if inDef and inDraw:
                input = " ".join(row)
                #print input
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

                    poly = Polygon(**data)
                    for i in range(0, len(points), 2):
                        poly.add(Point(points[i], points[i + 1]))
                    output = poly.render()

                # Rectangle
                elif type == 'S':
                    data = dict(zip(['x1', 'y1', 'x2', 'y2', 'unit', 'representation', 'width', 'fill'], row))

                    rect = Rectangle(**data)
                    output = rect.render()

                # Circle
                elif type == 'C':
                    data = dict(zip(['x', 'y', 'radius', 'unit', 'representation', 'width', 'fill'], row))

                    circ = Circle(**data)
                    output = circ.render()

                # Arc
                elif type == 'A':
                    data = dict(zip(['x', 'y', 'radius', 'startAngle', 'endAngle', 'unit', 'representation', 'width', 'fill', 'startX', 'startY', 'endX', 'endY'], row))

                    arc = Arc(**data)
                    output = arc.render()

                # Text
                elif type == 'T':
                    row.pop(4) # Pop unused argument
                    data = dict(zip(['orientation', 'x', 'y', 'size', 'unit', 'representation', 'text', 'italic', 'bold', 'hjustify', 'vjustify'], row))

                    text = Text(**data)
                    output = text.render()

                # Pin
                elif type == 'X':
                    data = dict(zip(['name', 'number', 'x', 'y', 'length', 'orientation', 'numberSize', 'nameSize', 'unit', 'representation', 'type', 'shape'], row))

                    p = Pin_(**data)
                    output = p.render()

                print output
                #if input == output:
                #    print "PASS"
                #else:
                #    print "FAILED"
                #print

    def replaceLoad(self, filename, unit, map):
        file = open(filename, "r")
        text = re.sub('^#.*$\s*', '', file.read(), 0, re.M)
        file.close()

        rep_map = {}
        for key, value in map.iteritems():
            if type(value) is str:
                rep_map[key.upper()] = value.replace(' ', '~')
            else:
                rep_map[key.upper()] = value
        print rep_map

        text = re.sub("\$(\w+)", lambda m: rep_map[m.group(1)] if m.group(1) in rep_map else m.group(0), text)
        print text

        text = StringIO.StringIO(text)

        inDef = False
        inDraw = False
        for row in csv.reader(text, delimiter = " ", skipinitialspace = True):
            if row[0] == 'DEF':
                inDef = True
            elif row[0] == 'DRAW':
                inDraw = True
                continue
            elif row[0] == 'ENDDEF':
                inDef = False
            elif row[0] == 'ENDDRAW':
                inDraw = False

            if inDef and inDraw:
                input = " ".join(row)
                #print input
                for i in range(len(row)):
                   try:
                       row[i] = int(row[i])
                   except:
                       pass

                output = ""
                symbol_type = row[0]
                row.pop(0)
                # Polygon
                if symbol_type == 'P':
                    data = dict(zip(['unit', 'representation', 'width', 'fill'], row[1:4]+row[-1:]))
                    if unit != -1:
                        data['unit'] = unit

                    points = row[4:-1]

                    poly = Polygon(**data)
                    for i in range(0, len(points), 2):
                        poly.add(Point(points[i], points[i + 1]))
                    self.modules.append(poly)
                #   output = poly.render()

                # Rectangle
                elif symbol_type == 'S':
                    data = dict(zip(['x1', 'y1', 'x2', 'y2', 'unit', 'representation', 'width', 'fill'], row))
                    if unit != -1:
                        data['unit'] = unit

                    self.modules.append(Rectangle(**data))
                #   output = rect.render()

                # Circle
                elif symbol_type == 'C':
                    data = dict(zip(['x', 'y', 'radius', 'unit', 'representation', 'width', 'fill'], row))
                    if unit != -1:
                        data['unit'] = unit

                    self.modules.append(Circle(**data))
                #   output = circ.render()

                # Arc
                elif symbol_type == 'A':
                    data = dict(zip(['x', 'y', 'radius', 'startAngle', 'endAngle', 'unit', 'representation', 'width', 'fill', 'startX', 'startY', 'endX', 'endY'], row))
                    if unit != -1:
                        data['unit'] = unit

                    self.modules.append(Arc(**data))
                #   output = arc.render()

                # Text
                elif symbol_type == 'T':
                    row.pop(4) # Pop unused argument
                    data = dict(zip(['orientation', 'x', 'y', 'size', 'unit', 'representation', 'text', 'italic', 'bold', 'hjustify', 'vjustify'], row))
                    if unit != -1:
                        data['unit'] = unit

                    self.modules.append(Text(**data))
                #   output = text.render()

                # Pin
                elif symbol_type == 'X':
                    data = dict(zip(['name', 'number', 'x', 'y', 'length', 'orientation', 'numberSize', 'nameSize', 'unit', 'representation', 'type', 'shape'], row))
                    if unit != -1:
                        data['unit'] = unit

                    self.modules.append(Pin_(**data))
                #   output = p.render()

    def optimize(self):
        """Detect duplicate graphical elements from symbol and merge them to unit = 0"""
        list = []
        for a, b in itertools.combinations(self.modules, 2):
            if a == b:
                print "Equal: ", a, b
                a.unit = 0
                list.append(b)

        print "self.modules"
        for module in self.modules:
            print module
        print

        print "list"
        for module in list:
            print module
        print

        #lists = set(list)
        test = [item for item in self.modules if item not in list]
        print "test"
        for module in test:
            print module
        print

        for module in self.modules:
            print module.render()


    def render(self, packageList = None):
        """Build the symbol representation.

        The result is a list of strings.
        """
        valueFieldPos = self.valueFieldPos()
        refFieldPos = self.refFieldPos()

        moduleList = map(lambda x : x.render(self.name, valueFieldPos[0], self.nameCentered), self.modules)
        result = [ Symbol.DefFormat%(self.name, self.ref, len(self.modules)),
                Symbol.RefFieldFormat%(self.ref, refFieldPos[0], refFieldPos[1]),
                Symbol.ValueFieldFormat%(self.name, valueFieldPos[0], valueFieldPos[1])]
        if self.footprint != None:
            if self.footprint != "":
                result.append(Symbol.FootprintFieldFormat%(self.footprint))
        if packageList != None:
            result.append("$FPLIST")
            result.extend(packageList)
            result.append("$ENDFPLIST")
        result.append("DRAW")
        for x in moduleList:
            result.extend(x)
        result.extend( ["ENDDRAW","ENDDEF"] )
        return result
