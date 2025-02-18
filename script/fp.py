#!/usr/bin/python
#
# Copyright (c) 2015 Benjamin Fueldner
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
# Defines footprint elements in new S-format/syntax

import time
import math
import config

cfg = config.Config("config")

registry = {}

class metaclass_register(type):
    def __init__(self, name, bases, nmspc):
        super(metaclass_register, self).__init__(name, bases, nmspc)
        registry[name] = self

class technology():
    smd = "smd"
    connector = "TBD"
    thru_hole = "thru_hole"
    non_plated = "TBD"

class type():
    circle = "circle"
    oval = "oval"
    rect = "rect"
    trapezoid = "trapezoid"


class text():
    """Generate text at x/y"""
    format = """  (fp_text %s %s (at %.3f %.3f %.3f) (layer %s)
    (effects (font (size %.3f %.3f) (thickness %.3f)))
  )\n"""

    def __init__(self, layer, name, value, x, y, angle, size, thickness):
        self.layer = layer
        self.name = name
        self.value = value
        self.x = x
        self.y = y
        self.angle = angle
        self.size = size
        self.thickness = thickness

    def render(self):
        return text.format%(self.name, self.value, self.x, self.y, self.angle, self.layer, self.size, self.size, self.thickness)

class line():
    """Generate line from x1/y1 to x2/y2"""
    format = "  (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width %.3f))\n"

    def __init__(self, layer, x1, y1, x2, y2, width):
        self.layer = layer
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width

    def render(self):
        return line.format%(self.x1, self.y1, self.x2, self.y2, self.layer, self.width)

class arc():
    """Generate arc between x1/y1 and x2/y2 with given angle"""

    format = "  (fp_arc (start %.3f %.3f) (end %.3f %.3f) (angle %.3f) (layer %s) (width %.3f))\n"

    def __init__(self, layer, x1, y1, x2, y2, angle, width):
        self.layer = layer
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.angle = angle
        self.width = width

    def area(self):
        return {'x1': self.x1, 'y1': self.y1, 'x2': self.x2, 'y2': self.y2}

    def render(self):
        return arc.format%(self.x1, self.y1, self.x2, self.y2, self.angle, self.layer, self.width)

class circle():
    """Generate circle with center x1/y1 and radius through point x2/y2"""

    format = "  (fp_circle (center %.3f %.3f) (end %.3f %.3f) (layer %s) (width %.3f))\n"

    def __init__(self, layer, x1, y1, x2, y2, width):
        self.layer = layer
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width

    def render(self):
        return circle.format%(self.x1, self.y1, self.x2, self.y2, self.layer, self.width)

class rectangle():
    """Generate rectangle on given layer"""

    def __init__(self, layer, x, y, width, height, line_width, centered = False):
        if centered:
            x -= width / 2
            y -= height / 2

        self.elements = []
        self.elements.append(line(layer, x, y, x + width, y, line_width))
        self.elements.append(line(layer, x + width, y, x + width, y + height, line_width))
        self.elements.append(line(layer, x + width, y + height, x, y + height, line_width))
        self.elements.append(line(layer, x, y + height, x, y, line_width))

    def render(self):
        result = ""
        for element in self.elements:
            result += element.render()
        return result

class beveled_rectangle():
    """Rectangle with beveled edges"""

    def __init__(self, layer, x, y, width, height, bevel, line_width, centered = False):
        if centered:
            x -= width / 2
            y -= height / 2

        self.elements = []
        self.elements.append(line(layer, x + bevel, y, x + width - bevel, y, line_width))                            # -
        self.elements.append(line(layer, x + width - bevel, y, x + width, y + bevel, line_width))                    # \
        self.elements.append(line(layer, x + width, y + bevel, x + width, y + height - bevel, line_width))           # |
        self.elements.append(line(layer, x + width, y + height - bevel, x + width - bevel, y + height, line_width))  # /
        self.elements.append(line(layer, x + width - bevel, y + height, x + bevel, y + height, line_width))          # -
        self.elements.append(line(layer, x + bevel, y + height, x, y + height - bevel, line_width))                  # \
        self.elements.append(line(layer, x, y + height - bevel, x, y + bevel, line_width))                           # |
        self.elements.append(line(layer, x, y + bevel, x + bevel, y, line_width))                                    # /

    def render(self):
        result = ""
        for element in self.elements:
            result += element.render()
        return result

class beveled_outline():
    """Outline with beveled corners every grid point"""

    def __init__(self, layer, x, y, width, height, bevel, grid, line_width, centered = False):
        if centered:
            x -= width / 2
            y -= height / 2

        self.elements = []

        x_rep = int(width / grid)
        y_rep = int(height / grid)
        for i in range(x_rep):
            if i != 0:
                self.elements.append(line(layer, i * grid + x, y + bevel, i * grid + x + bevel, y, line_width))
            self.elements.append(line(layer, i * grid + x + bevel, y, i * grid + x + grid - bevel, y, line_width))
            self.elements.append(line(layer, i * grid + x + grid - bevel, y, i * grid + x + grid, y + bevel, line_width))

        for i in range(y_rep):
            if i != 0:
                self.elements.append(line(layer, x + width - bevel, i * grid + y, x + width, i * grid + y + bevel, line_width))
            self.elements.append(line(layer, x + width, i * grid + y + bevel, x + width, i * grid + y + grid - bevel, line_width))
            self.elements.append(line(layer, x + width, i * grid + y + grid - bevel, x + width - bevel, i * grid + y + grid, line_width))

        for i in reversed(range(x_rep)):
            if i != (x_rep - 1):
                self.elements.append(line(layer, i * grid + x + grid, y + height - bevel, i * grid + x + grid - bevel, y + height, line_width))
            self.elements.append(line(layer, i * grid + x + grid - bevel, y + height, i * grid + x + bevel, y + height, line_width))
            self.elements.append(line(layer, i * grid + x + bevel, y + height, i * grid + x, y + height - bevel, line_width))

        for i in reversed(range(y_rep)):
            if i != (y_rep - 1):
                self.elements.append(line(layer, x + bevel, i * grid + y + grid, x, i * grid + y + grid - bevel, line_width))
            self.elements.append(line(layer, x, i * grid + y + grid - bevel, x, i * grid + y + bevel, line_width))
            self.elements.append(line(layer, x, i * grid + y + bevel, x + bevel, i * grid + y, line_width))

    def render(self):
        result = ""
        for element in self.elements:
            result += element.render()
        return result

class pad():
    """Generate pad in x/y with size width/height in given technology/type"""

    format = "  (pad %s %s %s (at %.3f %.3f %.3f) (size %.3f %.3f) %s(layers %s))\n"
    format_drill = "(drill %.3f) "

    def __init__(self, layers, name, tech, type, x, y, width, height, drill = 0, angle = 0):
        self.layers = layers
        self.name = name
        self.tech = tech
        self.type = type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if drill:
            self.drill = pad.format_drill%(drill)
        else:
            self.drill = ""
        self.angle = angle

    def render(self):
        return pad.format%(self.name, self.tech, self.type, self.x, self.y, self.angle, self.width, self.height, self.drill, self.layers)

# Base class for footprints
class base(object):
    __metaclass__ = metaclass_register

    def __init__(self, name, model, description = "", tags = "", smd = False, add_text = True):
        self.name = name
        self.model = model
        self.description = description
        self.tags = tags
        self.smd = smd
        self.elements = []

        if add_text:
            self.elements.append(text(cfg.FOOTPRINT_REFERENCE_LAYER, "reference", "REF**", 0, 0, 0, cfg.FOOTPRINT_REFERENCE_FONT_SIZE, cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS))
            self.elements.append(text(cfg.FOOTPRINT_VALUE_LAYER, "value", "VAL**", 0, cfg.FOOTPRINT_VALUE_FONT_SIZE + 2 * cfg.FOOTPRINT_VALUE_FONT_THICKNESS, 0, cfg.FOOTPRINT_VALUE_FONT_SIZE, cfg.FOOTPRINT_VALUE_FONT_THICKNESS))

    def add(self, element):
        self.elements.append(element)

    def remove(self, index):
        self.elements.remove(index)

    def render(self):
        result = '(module %s (tedit %.8X)\n'%(self.name, int(time.time()))
        if self.smd:
            result += '  (attr smd)\n'

        if len(self.description):
            result += '  (descr "'+self.description+'")\n'

        if len(self.tags):
            result += '  (tags "'+self.tags+'")\n'

        for element in self.elements:
            result += element.render()

        if len(self.model):
            result += '  (model '+self.model+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'

        result += ')\n'
        return result
