#!/usr/bin/python

import fp
from fp import cfg

try:
	from lxml import etree
	print("running with lxml.etree")
except ImportError:
	try:
	# Python 2.5
		import xml.etree.cElementTree as etree
		print("running with cElementTree on Python 2.5+")
	except ImportError:
		try:
		# Python 2.5
			import xml.etree.ElementTree as etree
			print("running with ElementTree on Python 2.5+")
		except ImportError:
			try:
			# normal cElementTree install
				import cElementTree as etree
				print("running with cElementTree")
			except ImportError:
				try:
				# normal ElementTree install
					import elementtree.ElementTree as etree
					print("running with ElementTree")
				except ImportError:
					print("Failed to import ElementTree from any known place")

ifile = open('PowerMagnetics.lbr', "r")
text = ifile.read()
ifile.close()

#import xml.sax
#
#class MiniHandler(xml.sax.handler.ContentHandler):
#	def startDocument(self):
#		print "ANFANG"
#
#	def endDocument(self):
#		print "ENDE"
#
#	def startElement(self, name, attrs):
#		print "Element", name
#
#	def characters(self, content):
#		s = content.strip()
#		if s != "":
#			print "Textinhalt:", s
#
#handler = MiniHandler()
#datei = open("PowerMagnetics.lbr", "r")
#xml.sax.parse(datei, handler)
#datei.close()

tree = etree.parse('PowerMagnetics.lbr')
root = tree.getroot()

layer_map = {}
for layer in root.iterfind(".//layer"):
	layer_map[int(layer.attrib['number'])] = layer.attrib['name']
#print layer_map

kicad_layer = {}
kicad_layer[27] = cfg.FOOTPRINT_VALUE_LAYER	# tValues
kicad_layer[25] = cfg.FOOTPRINT_REFERENCE_LAYER	# tNames
kicad_layer[21] = cfg.FOOTPRINT_PACKAGE_LAYER	# tPlace
kicad_layer[51] = cfg.FOOTPRINT_PACKAGE_LAYER	# tDocu
kicad_layer[39] = cfg.FOOTPRINT_PACKAGE_LAYER	# tKeepout
kicad_layer[43] = cfg.FOOTPRINT_PACKAGE_LAYER	# vRestrict

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
#	print("%s: %s" % (action, elem.tag))
