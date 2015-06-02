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

class type():
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
    inverted = "I"
    clock = "C"
    invertedClock = "CI"
    inputLow = "L"
    clockLow = "CL"
    outputLow = "V"
    fallingEdgeClock = "F"
    nonLogic = "X"

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

        for point1, point2 in zip(self.points, rhs.points):
            if point1 != point2:
                return False

        return True

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

    def __init__(self, name, ref, nameCentered, package = ""):
        """Creates a new symbol instance.

        name -- symbol name.
        ref -- kicad symbol reference string.
        nameCentered -- a boolean indicating if the name should be centered according to the symbol boundaries.
        """
        self.name = name
        self.ref = ref
        self.modules =[]
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

    def load(self, filename, unit = 0):
        """Load only graphic elements from a symbol file and add it to the given unit"""
        pass

    def optimize(self):
        """Detect duplicate graphical elements from symbol and merge them to unit = 0"""
        pass

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
