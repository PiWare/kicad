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
cfg = config.Config("config")

class Pin(object):
    """Represents a pin assigned to a schematic symbol."""

    FormatString = "X %s %i %i %i " + str(cfg.SYMBOL_PIN_LENGTH) + " %s " + str(cfg.SYMBOL_PIN_NUMBER_SIZE) + " " + str(cfg.SYMBOL_PIN_NAME_SIZE) + " %i %i %s"

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

    def getRep(self,x,y,orientation,group,convert):
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

    DefFormat="DEF %s %s 0 "+str(cfg.SYMBOL_PIN_TEXT_OFFSET)+" Y Y %i L N"
    RefFieldFormat = ( "F%i"%(cfg.REFERENCE_FIELD)
            + ' "%s" %i %i'
            + " " + str(cfg.SYMBOL_NAME_SIZE)
            + " H V C CNN")

    ValueFieldFormat = ( "F%i"%(cfg.VALUE_FIELD)
            + ' "%s" %i %i'
            + " " + str(cfg.SYMBOL_NAME_SIZE)
            + " H I C CNN")

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

    def getRep(self):
        """Build the symbol representation.

        The result is a list of strings.
        """
        if self.nameCentered == True:
            valueFieldXPos = -len(self.name)/4*cfg.SYMBOL_NAME_SIZE
            valueFieldYPos = cfg.SYMBOL_TEXT_MARGIN
            refFieldXPos = -(len(self.ref)+4)/4*cfg.SYMBOL_NAME_SIZE
            refFieldYPos = -cfg.SYMBOL_TEXT_MARGIN
        else:
            valueFieldXPos = (len(self.name)/2 + len(self.ref)+4)*cfg.SYMBOL_NAME_SIZE+cfg.SYMBOL_TEXT_MARGIN
            valueFieldYPos = cfg.SYMBOL_NAME_SIZE
            refFieldXPos = cfg.SYMBOL_TEXT_MARGIN
            refFieldYPos = valueFieldYPos

        moduleList = map(lambda x : x.getRep(self.name, valueFieldXPos, self.nameCentered), self.modules)
        result = [ Symbol.DefFormat%(self.name, self.ref, len(self.modules)),
                Symbol.RefFieldFormat%(self.ref, refFieldXPos, refFieldYPos),
                Symbol.ValueFieldFormat%(self.name, valueFieldXPos, valueFieldYPos),
                Symbol.FootprintFieldFormat%(self.footprint),
                "DRAW"]
        for x in moduleList:
            result.extend(x)
        result = result + ["ENDDRAW","ENDDEF"]
        return result
