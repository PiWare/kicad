#!/usr/bin/python

import itertools

class Item(object):
    "Base item for graphical symbol elements"

    def __init__(self, unit = 0, prio = 0):
        self.unit = unit
        self.prio = prio
        self.dup = 0

    def priority(self):
        return self.unit * 65536 + self.prio * 256

class Rectangle(Item):
    "Render rectangle"

    Format = "S %d %d %d %d %d"
    Prio = 1

    def __init__(self, x1, y1, x2, y2, unit = 0):
        super(Rectangle, self).__init__(unit, Rectangle.Prio)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        print "Rectangle, unit = ", unit
        print Rectangle.Format%(x1, y1, x2, y2, unit)

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Rectangle):
            return False

        return self.x1 == rhs.x1 and self.y1 == rhs.y1 and self.x2 == rhs.x2 and self.y2 == rhs.y2

    def render(self):
        print Rectangle.Format%(self.x1, self.y1, self.x2, self.y2, self.unit)
        return Rectangle.Format%(self.x1, self.y1, self.x2, self.y2, self.unit)

class Pin(Item):

    Format = "X %s %s %d %d %d"
    Prio = 10

    def __init__(self, x, y, name, number, unit = 0):
        super(Pin, self).__init__(unit, Pin.Prio)

        self.x = x
        self.y = y
        self.name = name
        # FIXME: Try another way if we use BGA (A1, B2, ...)
        try:
            self.number = int(number)
        except:
            self.number = number

    def equal(self, rhs):
        """Compare only graphical elements"""
        if not isinstance(rhs, Pin):
            return False

        return False

    def priority(self):
        try:
            return self.unit * 65536 + self.prio * 256 + self.number
        except:
            return self.unit * 65536 + self.prio * 256

    def render(self):
        return (Pin.Format%(self.name, self.number, self.x, self.y, self.unit)).rstrip()

modules = []
for unit in range(1, 5):
    print unit
    modules.append(Rectangle(-5, -5, 5, 5, unit))
    if unit < 4:
        modules.append(Rectangle(-10, -10, 10, 10, unit))
    modules.append(Pin(-5, -5, str(unit), unit, unit))

list = []
for a, b in itertools.combinations(modules, 2):
    print a, b
    if a.equal(b):
        a.dup += 1
        b.dup += 1
print

for item in modules:
    print item.dup
#        a.unit = 0
#        list.append(b)
