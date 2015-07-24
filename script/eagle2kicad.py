#!/usr/bin/python

import fp
import re
from fp import cfg
import argparse
from lxml import etree

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Convert Eagle xml library to KiCAD symbols/footprints.')
    parser.add_argument('-l', '--list', dest = "list", action = 'store_const', const = True, default = False, help = 'List all symbols/footprints')
    parser.add_argument('--harmonize', dest = "harmonize", action = 'store_const', const = True, default = False, help = 'Harmonize symbol/footprint to KiCAD configuration (font, line_with, ...)')
    parser.add_argument('--lbr', metavar = 'lbr', type = str, help = 'Eagle xml library (.lbr)', required = True)
#   parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
    parser.add_argument('--output_path', metavar = 'output_path', type = str, help = 'Output path for generated KiCAD footprint files', required = True)
#   parser.add_argument('--harmonize', metavar = 'harmonize', help = 'Harmonize symbol/footprint to KiCAD configuration (font, line_with, ...)', required = False)
#   parser.add_argument('-l', metavar = 'list', help = 'List all symbols/footprints', required = False)

#   parser.add_argument('move', choices=['rock', 'paper', 'scissors'])
    args = parser.parse_args()

#   file = open(args.lbr, "r")
#   lbr_text = file.read()
#   file.close()

    tree = etree.parse(args.lbr)
    root = tree.getroot()

    if args.list:
        print "Symbols:"
        for symbol in root.iterfind(".//symbol"):
        #   desc = package.find("description")
        #   if desc is not None:
        #       print re.sub('<[^<]+?>', '', desc.text)
        #   else:
        #       print "Keine Beschreibung"
            print symbol.attrib['name']

        print "\nFootprints:"

        for package in root.iterfind(".//package"):
        #   desc = package.find("description")
        #   if desc is not None:
        #       print re.sub('<[^<]+?>', '', desc.text)
        #   else:
        #       print "Keine Beschreibung"
            print package.attrib['name']
        exit()

    layer_map = {}
    for layer in root.iterfind(".//layer"):
        layer_map[int(layer.attrib['number'])] = layer.attrib['name']
    #print layer_map

    kicad_layer = {}
    kicad_layer[27] = cfg.FOOTPRINT_VALUE_LAYER      # tValues
    kicad_layer[25] = cfg.FOOTPRINT_REFERENCE_LAYER  # tNames
    kicad_layer[21] = cfg.FOOTPRINT_PACKAGE_LAYER    # tPlace
    kicad_layer[51] = cfg.FOOTPRINT_PACKAGE_LAYER    # tDocu
    kicad_layer[39] = cfg.FOOTPRINT_PACKAGE_LAYER    # tKeepout
    kicad_layer[43] = cfg.FOOTPRINT_PACKAGE_LAYER    # vRestrict

    #footprint = fp.base()
    footprint = []

    name = ""
    description = ""
    smd = False
    for package in root.iterfind(".//package"):
        print package.attrib['name']

        if package.attrib['name'] == 'S':
            name = package.attrib['name']
            for element in package:
                if element.tag == "description":
                    description = element.text
                elif element.tag == "smd":
                    param = {}
                    param['layers'] = cfg.FOOTPRINT_SMD_LAYERS
                    param['name'] = element.attrib['name']
                    param['tech'] = fp.technology.smd
                    param['type'] = fp.type.rect
                    param['x'] = float(element.attrib['x'])
                    param['y'] = float(element.attrib['y'])
                    param['width'] = float(element.attrib['dx'])
                    param['height'] = float(element.attrib['dy'])
                    param['drill'] = 0
                    param['angle'] = float(element.attrib['rot'].lstrip('R'))
                    footprint.append(fp.pad(**param))
                    smd = True
                elif element.tag == "text":
                    param = {}
                    param['x'] = float(element.attrib['x'])
                    param['y'] = float(element.attrib['y'])
                    if element.text == ">NAME":
                        param['name'] = "reference"
                        param['value'] = "REF**"
                        param['layer'] = cfg.FOOTPRINT_REFERENCE_LAYER
                        param['size'] = cfg.FOOTPRINT_REFERENCE_FONT_SIZE
                        param['thickness'] = cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS
                    elif element.text == ">VALUE":
                        param['name'] = "value"
                        param['value'] = "VAL**"
                        param['layer'] = cfg.FOOTPRINT_VALUE_LAYER
                        param['size'] = cfg.FOOTPRINT_VALUE_FONT_SIZE
                        param['thickness'] = cfg.FOOTPRINT_VALUE_FONT_THICKNESS
                    else:
                        param['name'] = "user"
                        param['value'] = element.text
                        param['layer'] = cfg.FOOTPRINT_USER_LAYER
                        param['size'] = cfg.FOOTPRINT_USER_FONT_SIZE
                        param['thickness'] = cfg.FOOTPRINT_USER_FONT_THICKNESS
                    footprint.append(fp.text(**param))
                elif element.tag == "wire":
                    param = {}
                    param['layer'] = kicad_layer[int(element.attrib['layer'])]
                    param['x1'] = float(element.attrib['x1'])
                    param['y1'] = float(element.attrib['y1'])
                    param['x2'] = float(element.attrib['x2'])
                    param['y2'] = float(element.attrib['y2'])
                    param['width'] = float(element.attrib['width'])
                    footprint.append(fp.line(**param))
                elif element.tag == "rectangle":
                    angle = int(element.attrib['rot'].lstrip('R'))
                    param = {}
                    param['layer'] = kicad_layer[int(element.attrib['layer'])]
                    if angle == 90:
                        param['x'] = float(element.attrib['y1'])
                        param['y'] = float(element.attrib['x1'])
                        param['width'] = float(element.attrib['y2']) - param['x']
                        param['height'] = float(element.attrib['x2']) - param['y']
                    else:
                        param['x'] = float(element.attrib['x1'])
                        param['y'] = float(element.attrib['y1'])
                        param['width'] = float(element.attrib['x2']) - param['x']
                        param['height'] = float(element.attrib['y2']) - param['y']
                    param['line_width'] = cfg.FOOTPRINT_PACKAGE_LINE_WIDTH
                    footprint.append(fp.rectangle(**param))
                else:
                    print element.tag, element.text
            break

    fprint = fp.base(name, description, "", smd, False)
    for element in footprint:
        fprint.add(element)
    print fprint.render()


    #events = ("start", "end")
    #context = etree.iterparse(text, events=events)
    #for action, elem in context:
    #    print("%s: %s" % (action, elem.tag))
