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

# This script contains commons object definitions to generate kicad footprints

import time
import csv
import config
cfg = config.Config("config")

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
	format = """  (fp_text %s %s (at %.3f %.3f) (layer %s)
	(effects (font (size %.3f %.3f) (thickness %.3f)))
  )"""

	def __init__(self, layer, name, value, x, y, size, thickness):
		self.layer = layer
		self.name = name
		self.value = value
		self.x = x
		self.y = y
		self.size = size
		self.thickness = thickness

	def render(self):
		print text.format%(self.name, self.value, self.x, self.y, self.layer, self.size, self.size, self.thickness)

class line():
	"""Generate line from x1/y1 to x2/y2"""
	format = "  (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width %.3f))"

	def __init__(self, layer, x1, y1, x2, y2, width):
		self.layer = layer
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.width = width

	def render(self):
		print line.format%(self.x1, self.y1, self.x2, self.y2, self.layer, self.width)

class arc():
	"""Generate arc between x1/y1 and x2/y2 with given angle"""

	format = "  (fp_arc (start %.3f %.3f) (end %.3f %.3f) (angle %.3f) (layer %s) (width %.3f))"

	def __init__(self, layer, x1, y1, x2, y2, angle, width):
		self.layer = layer
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.angle = angle
		self.width = width

	def render(self):
		print arc.format%(self.x1, self.y1, self.x2, self.y2, self.angle, self.layer, self.width)

class circle():
	"""Generate circle with center x1/y1 and radius through point x2/y2"""

	format = "  (fp_circle (center %.3f %.3f) (end %.3f %.3f) (layer %s) (width %.3f))"

	def __init__(self, layer, x1, y1, x2, y2, width):
		self.layer = layer
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.width = width

	def render(self):
		print circle.format%(self.x1, self.y1, self.x2, self.y2, self.layer, self.width)

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
		for element in self.elements:
			element.render()

class pad():
	"""Generate pad in x/y with size width/height in given technology/type"""

	format = "  (pad %s %s %s (at %.3f %.3f %.3f) (size %.3f %.3f) %s(layers %s))"
	format_drill = "(drill %.3f) "

	def __init__(self, layers, name, tech, type, x, y, width, height, angle = 0, drill = 0):
		self.layers = layers
		self.name = name
		self.tech = tech
		self.type = type
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.angle = angle
		if drill:
			self.drill = pad.format_drill%(drill)
		else:
			self.drill = ""

	def render(self):
		print pad.format%(self.name, self.tech, self.type, self.x, self.y, self.angle, self.width, self.height, self.drill, self.layers)

class footprint():
	def __init__(self, name, description = "", tags = "", smd = False):
		self.name = name
		self.description = description
		self.tags = tags
		self.smd = smd
		self.elements = []

		self.elements.append(text(cfg.FOOTPRINT_REFERENCE_LAYER, "reference", "REF**", 0, 0, cfg.FOOTPRINT_REFERENCE_FONT_SIZE, cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS))
		self.elements.append(text(cfg.FOOTPRINT_VALUE_LAYER, "value", "VAL**", 0, 1, cfg.FOOTPRINT_VALUE_FONT_SIZE, cfg.FOOTPRINT_VALUE_FONT_THICKNESS))

	def add(self, element):
		self.elements.append(element)

	def render(self):
		print '(module %s (tedit %.8X)'%(self.name, int(time.time()))
		if self.smd:
			print '  (attr smd)'

		if len(self.description):
			print '  (descr "'+self.description+'")'

		if len(self.tags):
			print '  (tags "'+self.tags+'")'

		for element in self.elements:
			element.render()

		print ')'

class chip(footprint):
	"""Generator for chip resistors, capacitors and inductors"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height):
		footprint.__init__(self, name, description, tags, True)
		self.package_width = package_width
		self.package_height = package_height
		self.pad_width = pad_width
		self.pad_height = pad_height
		footprint.add(self, rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))

class soic(footprint):
	"""Generator for small outline ICs"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, count):
		footprint.__init__(self, name, description, tags, True)

		if count % 2:
			raise NameError("pin count is odd")

		pin = 1
		x = pad_grid * -((count / 4) - 0.5)
		line_x = package_width / 2
		line_y = package_height / 2 - 0.5

		footprint.add(self, rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))
		footprint.add(self, line(cfg.FOOTPRINT_PACKAGE_LAYER, -line_x, line_y, line_x, line_y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))

		diff = -line_x - x
		line_y += diff
		footprint.add(self, circle(cfg.FOOTPRINT_PACKAGE_LAYER, x, line_y, x - 0.3, line_y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))
		for i in range(count / 2):
			footprint.add(self, pad(cfg.FOOTPRINT_SMD_LAYERS, pin, technology.smd, type.rect, x, pad_distance / 2, pad_width, pad_height, 0))
			x += pad_grid
			pin += 1

		for i in range(count / 2, count):
			x -= pad_grid
			footprint.add(self, pad(cfg.FOOTPRINT_SMD_LAYERS, pin, technology.smd, type.rect, x, -pad_distance / 2, pad_width, pad_height, 0))
			pin += 1

class dil(footprint):
	"""Generator for dual inline ICs"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, count, drill):
		footprint.__init__(self, name, description, tags)

		if count % 2:
			raise NameError("pin count is odd")

		pin = 1
		x = pad_grid * -((count / 4) - 0.5)
		line_x = package_width / 2

		footprint.add(self, rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))
		footprint.add(self, arc(cfg.FOOTPRINT_PACKAGE_LAYER, -line_x, 0, -line_x, 0.6, -180, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))
		for i in range(count / 2):
			footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, pin, technology.thru_hole, type.oval, x, pad_distance / 2, pad_width, pad_height, 0, drill))
			x += pad_grid
			pin += 1

		for i in range(count / 2, count):
			x -= pad_grid
			footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, pin, technology.thru_hole, type.oval, x, -pad_distance / 2, pad_width, pad_height, 0, drill))
			pin += 1

with open('data/footprint/soic.csv', 'rb') as csvfile:
	table = csv.reader(csvfile, delimiter=',', quotechar='\"')
	first_row = 1
	for row in table:
		if first_row == 1:
			header = row
			first_row = 0
		else:
			data = dict(zip(header, row))
			if data['generator'] == "soic":
				fp = soic(data['name'], data['description'], data['tags'], float(data['package_width']), float(data['package_height']), float(data['pad_width']), float(data['pad_height']), float(data['pad_grid']), float(data['pad_distance']), int(data['pad_count']))
			elif data['generator'] == "dil":
				fp = dil(data['name'], data['description'], data['tags'], float(data['package_width']), float(data['package_height']), float(data['pad_width']), float(data['pad_height']), float(data['pad_grid']), float(data['pad_distance']), int(data['pad_count']), float(data['pad_drill']))
			fp.render()
			del fp

#footprint_table['soic'](data['name'], data['description'], data['tags'], float(data['package_width']), float(data['package_height']), float(data['pad_width']), float(data['pad_height']), float(data['pad_grid']), float(data['pad_distance']), int(data['pad_count']))