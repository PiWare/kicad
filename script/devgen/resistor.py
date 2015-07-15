#!/usr/bin/python

import sys
import math
import itertools
import argparse

DECADE_START = 0
DECADE_END   = 8

erow_data = {   3: { 'tolerance':  20, 'precision': 1 },
           6: { 'tolerance':  20, 'precision': 1 },
          12: { 'tolerance':  10, 'precision': 1 },
          24: { 'tolerance':   5, 'precision': 1 },
          48: { 'tolerance':   2, 'precision': 2 },
          96: { 'tolerance':   1, 'precision': 2 },
         192: { 'tolerance': 0.5, 'precision': 2 }}

char = ['R', 'R', 'R', 'k', 'k', 'k', 'M', 'M', 'M']

footprint_data = {
    'chip_resistor_0201': { 'power': 0.05,  'type': 'smd' },
    'chip_resistor_0402': { 'power': 0.063, 'type': 'smd' },
    'chip_resistor_0603': { 'power': 0.1,   'type': 'smd' },
    'chip_resistor_0805': { 'power': 0.125, 'type': 'smd' },
    'chip_resistor_1206': { 'power': 0.25,  'type': 'smd' },
    'chip_resistor_1210': { 'power': 0.5,   'type': 'smd' },
    'wire_10mm':          { 'power': 0.25,  'type': None },
    'melf':               { 'power': 1,     'type': None },
    'melf_mini':          { 'power': 0.4,   'type': None },
    'melf_micro':         { 'power': 0.3,   'type': None }}

def resistor(erow, index, decade):
    precision = erow_data[erow]['precision']
    result = math.pow(math.pow(10, float(1) / erow), index)
    result = round(result, precision)
    if erow <= 24:
        if result >= 2.6 and result <= 4.6:
            result += 0.1
        else:
            if result == 8.3:
                result -= 0.1

    result *= math.pow(10, decade % 3)
    precision -= decade % 3
    if precision < 0:
        precision = 0

    parts = str(result).split('.')
    if len(parts[1]) > precision:
        parts[1] = parts[1][:precision]
    elif len(parts[1]) < precision:
        parts[1] = parts[1].ljust(precision, '0')

    result = parts[0]+char[decade]+parts[1]
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Resistor table generator')
    parser.add_argument('--erow', type = int, nargs = "+", help = 'E-Row to generate (3, 6, 12, 24, 48, 96, 192)', required = True)
    parser.add_argument('--footprint', type = str, nargs = "+", help = 'Footprint (chip_resistor_0201, chip_resistor_0402, chip_resistor_0603, chip_resistor_0805, chip_resistor_1206, chip_resistor_1210, wire_10mm, melf, melf_mini, melf_micro)', required = True)
    parser.add_argument('--output_file', type = str, help = 'Output file for generated table', required = True)
    args = parser.parse_args()

    with open(args.output_file, 'w') as outfile:
        line = ["symbol", "name", "reference", "footprint", "description", "keywords", "1", "2", "value", "tolerance", "power"]
        outfile.write(','.join(line)+'\n')

        for footprint in args.footprint:
            if not footprint in footprint_data:
                print "FOOTPRINT value '%s' is invalid!"%(footprint)
                sys.exit(2)

            for erow in args.erow:
                if not erow in erow_data:
                    print "EROW value '%s' is invalid!"%(erow)
                    sys.exit(2)

                for decade in range(DECADE_START, DECADE_END):
                    for index in range(0, erow):
                        value = resistor(erow, index, decade)
                        tolerance = str(erow_data[erow]['tolerance'])+"%"
                        power = str(footprint_data[footprint]['power'])+"W"
                        name = "resistor_"+value+"_"+tolerance+"_"+power+"_"+footprint
                        description = "Resistor %s %s %s"%(value, tolerance, power)
                        keywords = 'resistor'
                        if footprint_data[footprint]['type']:
                            keywords += ', '+footprint_data[footprint]['type']
                        line = ["resistor", name, "R", footprint, description, '"'+keywords+'"', "1", "2", value, tolerance, power]
                        outfile.write(','.join(line)+'\n')

                        if index == 0 and decade == DECADE_END - 1:
                            break
        outfile.close()
