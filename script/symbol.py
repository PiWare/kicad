#!/usr/bin/python
#
# Copyright (C) 2015 Thomas Bernard and Benjamind Fueldner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# This script contains commons object definitions to generate kicad symbols

import config
import sys
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

class Field(object):
    """Symbol field"""

    Format = "F%d \"%s\" %d %d %d %s %s %s %s%s \"%s\""
    Map = {}
    for value in cfg.dict():
        part = value.split("_", 1)
        if len(part) == 2 and part[1] == 'FIELD':
            Map[int(getattr(cfg, value))] = getattr(cfg, part[0]+"_NAME")

    def __init__(self, number, value, x, y, size, orientation, visibility = visibility.visible, hjustify = hjustify.center, vjustify = vjustify.center, style = style.none):
        self.number = number
        self.value = value
        self.x = x
        self.y = y
        self.size = size
        self.orientation = orientation
        self.visibility = visibility
        self.hjustify = hjustify
        self.vjustify = vjustify
        self.style = style
        self.comment = Field.Map[number]

    def setValue(self, value):
        self.value = value

    def render(self):
        return Field.Format%(self.number, self.value, self.x, self.y, self.size, self.orientation, self.visibility, self.hjustify, self.vjustify, self.style, self.comment)

class Point(object):
    "Represents a point"

    Format = "%d %d"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Point):
            return False

        return self.x == rhs.x and self.y == rhs.y

    def render(self):
        return Point.Format%(self.x, self.y)

class Item(object):
    "Base item for graphical symbol elements"

    def __init__(self, unit = 0, representation = representation.normal, prio = 0):
        self.unit = unit
        self.representation = representation
        self.prio = prio

    def priority(self):
        return self.unit * 65536 + self.prio * 256

class Polygon(Item):
    "Render polygon"

    Format = "P %d %d %d %d %s%s"
    Prio = 2

    def __init__(self, width, fill = fill.background, unit = 0, representation = representation.normal):
        super(Polygon, self).__init__(unit, representation, Polygon.Prio)

        self.width = width
        self.fill = fill
        self.points = []

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Polygon):
            return False

        if len(self.points) != len(rhs.points):
            return False

        for point1, point2 in zip(self.points, rhs.points):
            if not point1.equal(point2):
                return False

        return True

    def add(self, point):
        self.points.append(point)

    def priority(self):
        return self.unit * 65536 + self.prio * 256 + len(self.points)

    def render(self):
        pts = ""
        for point in self.points:
            pts += point.render() + " "
        return Polygon.Format%(len(self.points), self.unit, self.representation, self.width, pts, self.fill)

class Rectangle(Item):
    "Render rectangle"

    Format = "S %d %d %d %d %d %d %d %s"
    Prio = 1

    def __init__(self, x1, y1, x2, y2, width, fill = fill.background, unit = 0, representation = representation.normal):
        super(Rectangle, self).__init__(unit, representation, Rectangle.Prio)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width
        self.fill = fill

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Rectangle):
            return False

        return self.x1 == rhs.x1 and self.y1 == rhs.y1 and self.x2 == rhs.x2 and self.y2 == rhs.y2

    def render(self):
        return Rectangle.Format%(self.x1, self.y1, self.x2, self.y2, self.unit, self.representation, self.width, self.fill)

class Circle(Item):
    "Render circle"

    Format = "C %d %d %d %d %d %d %s"
    Prio = 3

    def __init__(self, x, y, radius, width, fill = fill.background, unit = 0, representation = representation.normal):
        super(Circle, self).__init__(unit, representation, Circle.Prio)

        self.x = x
        self.y = y
        self.radius = radius
        self.width = width
        self.fill = fill

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Circle):
            return False

        return self.x == rhs.x and self.y == rhs.y and self.radius == rhs.radius

    def render(self):
        return Circle.Format%(self.x, self.y, self.radius, self.unit, self.representation, self.width, self.fill)

class Arc(Item):
    "Render arc"

    Format = "A %d %d %d %d %d %d %d %d %s %d %d %d %d"
    Prio = 4

    def __init__(self, x, y, startX, startY, endX, endY, startAngle, endAngle, radius, width, fill = fill.background, unit = 0, representation = representation.normal):
        super(Arc, self).__init__(unit, representation, Arc.Prio)

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

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Circle):
            return False

        return self.x == rhs.x and self.y == rhs.y and self.radius == rhs.radius

    def render(self):
        return Arc.Format%(self.x, self.y, self.radius, self.startAngle, self.endAngle, self.unit, self.representation, self.width, self.fill, self.startX, self.startY, self.endX, self.endY)

class Text(Item):
    """Format text element
        x, y - Position
        text - Text
        size - Size in mil
        orientation - Angle in centidegree (supported, but not documented!)
        unit - Unit number
        convert - Shape number
    """

    Format = 'T %d %d %d %d 0 %d %d %s %s %s %s %s'
    Prio = 0

    def __init__(self, x, y, text, size, orientation = 0, unit = 0, representation = representation.normal, italic = italic.off, bold = bold.off, hjustify = hjustify.center, vjustify = vjustify.center):
        super(Text, self).__init__(unit, representation, Text.Prio)

        self.x = x
        self.y = y
        self.text = text.replace(' ', '~')
        self.size = size
        self.orientation = orientation
        self.italic = italic
        self.bold = bold
        self.hjustify = hjustify
        self.vjustify = vjustify

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Text):
            return False

        return self.x == rhs.x and self.y == rhs.y and self.text == rhs.text

    def render(self):
        return Text.Format%(self.orientation, self.x, self.y, self.size, self.unit, self.representation, self.text, self.italic, self.bold, self.hjustify, self.vjustify)

class Pin_(Item):

    Format = "X %s %s %d %d %d %s %d %d %d %d %s %s"
    Prio = 10

    def __init__(self, x, y, name, number, length, orientation, nameSize, numberSize, unit = 0, representation = representation.normal, type = Type.input, shape = shape.line):
        super(Pin_, self).__init__(unit, representation, Pin_.Prio)

        self.x = x
        self.y = y
        self.name = name
        self.number = number
        self.length = length
        self.orientation = orientation
        self.nameSize = nameSize
        self.numberSize = numberSize
        self.type = type
        self.shape = shape

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Pin_):
            return False

        return False

    def priority(self):
        try:
            return self.unit * 65536 + self.prio * 256 + self.number
        except:
            return self.unit * 65536 + self.prio * 256

    def render(self):
        return (Pin_.Format%(self.name, self.number, self.x, self.y, self.length, self.orientation, self.numberSize, self.nameSize, self.unit, self.representation, self.type, self.shape)).rstrip()

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
        self.unit = 0

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
    Format = "DEF %s %s 0 %i %s %s %i %s %s"

    def __init__(self, name = "", reference = "", nameCentered = True, package = ""):
        """Creates a new symbol instance.

        name -- symbol name.
        ref -- kicad symbol reference string.
        nameCentered -- a boolean indicating if the name should be centered according to the symbol boundaries.
        """
        self.name = name
        self.reference = reference
        self.alias = []
        self.fields = {}
        self.modules = []
        self.descriptions = {}
        self.nameCentered = nameCentered
        self.footprint = package
        self.units = 0
        self.files = []

    def addModule(self, module):
        """Inserts a new module to the symbol. Returns the newly added module instance."""
        self.units = max(self.units, module.unit)
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

    def load(self, filename, unit = 0, representation = representation.both, map = {}, header = False):
        """Load graphic elements from a symbol file and add it to the given unit
            filename - Load given filename
            unit - Change loaded symbol elements to given unit. If unit = -1, no changes will be made.
            representation - Change loaded symbol elements to given representation.
            map - Text starting with dollar sign will be replaced with corresponding value.
            header - Load DEF and F# parts from file. Otherwise only graphic elements are taken.
        """

        if filename not in self.files:
            self.files.append(filename)

        file = open(filename, "r")
        text = re.sub('^#.*$\s*', '', file.read(), 0, re.M)
        file.close()

        rep_map = {}
        for key, value in map.iteritems():
            if type(value) is str:
                rep_map[key.upper()] = value.replace(' ', '~')
            else:
                rep_map[key.upper()] = value

        text = re.sub("\$(\w+)", lambda m: rep_map[m.group(1)] if m.group(1) in rep_map else m.group(0), text)
        text = StringIO.StringIO(text)

        inDef = False
        inDraw = False
        for row in csv.reader(text, delimiter = " ", skipinitialspace = True):
            if row[0] == 'EESchema-LIBRARY':
                if row[2] != '2.3':
                    print "Symbol version %s is not supported yet!"%(row[2])
                    sys.exit(2)
            elif row[0] == 'DEF':
                inDef = True
            elif row[0] == 'DRAW':
                inDraw = True
                continue
            elif row[0] == 'ENDDEF':
                inDef = False
            elif row[0] == 'ENDDRAW':
                inDraw = False

            for i in range(len(row)):
               try:
                   row[i] = int(row[i])
               except:
                   pass

            if inDef and not inDraw:
                if header:
                    if row[0] == 'DEF':
                        row.pop(0)
                        self.name = row[0]
                        self.reference = row[1]
                        self.offset = row[3]
                        self.pinnumber = row[4]
                        self.pinname = row[5]
                        self.count = 0 # = highest unit if != 0
                        self.locked = False # False, if no component part in unit = 0
                        self.flag = row[8]
                    else:
                        m = re.match(r"F(\d+)", row[0])
                        if m:
                            row.pop(0)
                            data = dict(zip(['value', 'x', 'y', 'size', 'orientation', 'visibility', 'hjustify', 'vjustify'], row))
                            data['style'] = data['vjustify'][1:]
                            data['vjustify'] = data['vjustify'][0]
                            data['number'] = int(m.group(1))

                            self.fields[int(m.group(1))] = Field(**data)

            elif inDef and inDraw:
                symbol_type = row[0]
                row.pop(0)
                # Polygon
                if symbol_type == 'P':
                    data = dict(zip(['unit', 'representation', 'width', 'fill'], row[1:4]+row[-1:]))
                    if unit != -1:
                        data['unit'] = unit
                    data['representation'] = representation

                    points = row[4:-1]

                    poly = Polygon(**data)
                    for i in range(0, len(points), 2):
                        poly.add(Point(points[i], points[i + 1]))
                    self.addModule(poly)

                # Rectangle
                elif symbol_type == 'S':
                    data = dict(zip(['x1', 'y1', 'x2', 'y2', 'unit', 'representation', 'width', 'fill'], row))
                    if unit != -1:
                        data['unit'] = unit
                    data['representation'] = representation

                    self.addModule(Rectangle(**data))

                # Circle
                elif symbol_type == 'C':
                    data = dict(zip(['x', 'y', 'radius', 'unit', 'representation', 'width', 'fill'], row))
                    if unit != -1:
                        data['unit'] = unit
                    data['representation'] = representation

                    self.addModule(Circle(**data))

                # Arc
                elif symbol_type == 'A':
                    data = dict(zip(['x', 'y', 'radius', 'startAngle', 'endAngle', 'unit', 'representation', 'width', 'fill', 'startX', 'startY', 'endX', 'endY'], row))
                    if unit != -1:
                        data['unit'] = unit
                    data['representation'] = representation

                    self.addModule(Arc(**data))

                # Text
                elif symbol_type == 'T':
                    row.pop(4) # Pop unused argument
                    data = dict(zip(['orientation', 'x', 'y', 'size', 'unit', 'representation', 'text', 'italic', 'bold', 'hjustify', 'vjustify'], row))
                    if unit != -1:
                        data['unit'] = unit
                    data['representation'] = representation

                    self.addModule(Text(**data))

                # Pin
                elif symbol_type == 'X':
                    data = dict(zip(['name', 'number', 'x', 'y', 'length', 'orientation', 'numberSize', 'nameSize', 'unit', 'representation', 'type', 'shape'], row))
                    if unit != -1:
                        data['unit'] = unit
                    data['representation'] = representation

                    self.addModule(Pin_(**data))

        # Overwrite properties, if defined in map
        if header:
            if 'name' in map:
                self.name = map['name']
            if 'reference' in map:
                self.reference = map['reference']
            if 'alias' in map:
                self.alias = map['alias'].split()

    def optimize(self):
        """Remove empty fields and detect duplicate graphical elements from symbol and merge them to unit = 0"""
        list = []
        for key, field in self.fields.iteritems():
            if not len(field.value):
                list.append(key)
        self.fields = { key: self.fields[key] for key in self.fields if key not in list }

        list = []
        for a, b in itertools.combinations(self.modules, 2):
            if a.equal(b):
                a.unit = 0
                list.append(b)

        self.modules = [item for item in self.modules if item not in list]

    def setFields(self, map):
        for key, value in map.iteritems():
            ukey = key.upper()
            if hasattr(cfg, ukey+"_NAME") and hasattr(cfg, ukey+"_FIELD"):
                id = int(getattr(cfg, ukey + "_FIELD"))
                if id in self.fields:
                    self.fields[id].setValue(value)
                else:
                    print "Field %d (%s) not defined in symbol"%(id, getattr(cfg, ukey + "_NAME"))
                    return False
        return True

    def setDescriptions(self, map):
        if 'description' in map:
            self.descriptions['D'] = map['description'].translate(None, "\n\r")
        if 'keywords' in map:
            self.descriptions['K'] = map['keywords'].translate(None, "\n\r")
        if 'document' in map:
            self.descriptions['F'] = map['document'].translate(None, "\n\r")

    def renderSymbol(self):
        """Render symbol"""
        locked = "L"
        count = 1
        if self.units != 0:
            count = self.units
            # If all parts are loaded from the same file, we should have a swapable device!
            if len(self.files) == 1:
                locked = "F"

        result = [ "#", "# "+self.name, "#", Symbol.Format%(self.name, self.reference, self.offset, self.pinnumber, self.pinname, count, locked, self.flag) ]
        for key, field in self.fields.iteritems():
            result.append(field.render())

        if len(self.alias):
            result.append("ALIAS "+" ".join(self.alias))

        result.append("DRAW")
        for module in sorted(self.modules, key = lambda x: x.priority()):
            result.append(module.render())

        result.extend(["ENDDRAW", "ENDDEF", ""])
        return result

    def renderDescription(self):
        """Render description for symbol and all aliases"""
        base = []
        for key, description in self.descriptions.iteritems():
            base.append(key+" "+description)
        base.append("$ENDCMP")
        result = [ "#", "# "+self.name, "#", "$CMP "+self.name] + base
        for alias in self.alias:
            result += [ "#", "# "+alias, "#", "$CMP "+alias] + base
        result.append("")
        return result

    def render(self, packageList = None):
        """Build the symbol representation.

        The result is a list of strings.
        """
        valueFieldPos = self.valueFieldPos()
        refFieldPos = self.refFieldPos()

        moduleList = map(lambda x : x.render(self.name, valueFieldPos[0], self.nameCentered), self.modules)
        result = [ Symbol.DefFormat%(self.name, self.reference, len(self.modules)),
                Symbol.RefFieldFormat%(self.reference, refFieldPos[0], refFieldPos[1]),
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
