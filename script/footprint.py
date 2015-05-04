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

class Counter(dict):
	def __missing__(self, key):
		return 0

class Text():
	Format = """  (fp_text %s %s (at %.3f %.3f) (layer %s)
	(effects (font (size %.3f %.3f) (thickness %.3f)))
  )"""
	def __init__(self, name, value, x, y, layer, size, thickness):
		self.name = name
		self.value = value
		self.x = x
		self.y = y
		self.layer = layer
		self.size = size
		self.thickness = thickness

	def Render(self):
		print Text.Format%(self.name, self.value, self.x, self.y, self.layer, self.size, self.size, self.thickness)

class Line():
	Format = "  (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width %.3f))"
	def __init__(self, x1, y1, x2, y2, layer, width):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.layer = layer
		self.width = width

	def Render(self):
		print Line.Format%(self.x1, self.y1, self.x2, self.y2, self.layer, self.width)

class Rectangle():
	"""Render rectangle on given layer"""
	def __init__(self, x, y, width, height, layer, line_width, centered = False):
	#	self.x = x
	#	self.y = y
	#	self.width = width
	#	self.height = height
	#	self.layer = layer
		if centered:
			x -= width / 2
			y -= height / 2

		self.elements = []
		self.elements.append(Line(x, y, x + width, y, layer, line_width))
		self.elements.append(Line(x + width, y, x + width, y + height, layer, line_width))
		self.elements.append(Line(x + width, y + height, x, y + height, layer, line_width))
		self.elements.append(Line(x, y + height, x, y, layer, line_width))

	def Render(self):
		for element in self.elements:
			element.Render()

class Pad():
	Format = "  (pad %s smd rect (at %.3f %.3f) (size %.3f %.3f) (layers %s))"
	def __init__(self, name, x, y, width, height, layers):
		self.name = name
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.layers = layers
	#	self.type = "smd rect"

	def Render(self):
		print Pad.Format%(self.name, self.x, self.y, self.width, self.height, self.layers)

class Footprint():
	def __init__(self, name, description = "", tags = "", smd = False):
		self.name = name
		self.description = description
		self.tags = tags
		self.smd = smd
		self.elements = []

		self.elements.append(Text("reference", "REF**", 0, 0, "F.SilkS", 1.5, 1))
		self.elements.append(Text("value", "VAL**", 0, 1, "F.Fab", 1.5, 1))

	def AddElement(self, element):
		self.elements.append(element)

	def Render(self):
		print '(module %s (tedit %.8X)'%(self.name, int(time.time()))
		if self.smd:
			print '  (attr smd)'

		if len(self.description):
			print '  (descr "'+self.description+'")'

		if len(self.tags):
			print '  (tags "'+self.tags+'")'

		for element in self.elements:
			element.Render()

		print ')'

class chip(Footprint):
	"""Generator for chip resistors, capacitors and inductors"""
	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height):
		Footprint.__init__(self, name, description, tags, True)
		self.package_width = package_width
		self.package_height = package_height
		self.pad_width = pad_width
		self.pad_height = pad_height
		Footprint.AddElement(self, Rectangle(0, 0, package_width, package_height, "F.SilkS", 0.1, True))

class soic(Footprint):
	"""Generator for small outline ICs"""
	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, count):
		Footprint.__init__(self, name, description, tags, True)

		if count % 2:
			raise NameError("pin count is odd")

		pin = 1
		x = pad_grid * -((count / 4) - 0.5)
		Footprint.AddElement(self, Rectangle(0, 0, package_width, package_height, "F.SilkS", 0.1, True))
		for i in range(count / 2):
			Footprint.AddElement(self, Pad(pin, x, pad_distance / 2, pad_height, pad_width, "F.Cu F.Paste F.Mask"))
			x += pad_grid
			pin += 1

		for i in range(count / 2, count):
			x -= pad_grid
			Footprint.AddElement(self, Pad(pin, x, -pad_distance / 2, pad_height, pad_width, "F.Cu F.Paste F.Mask"))
			pin += 1

class dil(Footprint):
	"""Generator for dual inline ICs"""
	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height):
		Footprint.__init__(self, name, description, tags)
		self.package_width = package_width
		self.package_height = package_height
		self.pad_width = pad_width
		self.pad_height = pad_height
		Footprint.AddElement(self, Rectangle(0, 0, package_width, package_height, "F.SilkS", 0.1, True))

with open('data/footprint/soic.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='\"')
	first_row = 1
	for row in spamreader:
		if first_row == 1:
			header = row
			first_row = 0
		else:
			data = dict(zip(header, row))
			fp = soic(data['name'], data['description'], data['tags'], float(data['package_width']), float(data['package_height']), float(data['pad_width']), float(data['pad_height']), float(data['pad_grid']), float(data['pad_distance']), int(data['pad_count']))
			fp.Render()
			del fp

	#	for col in row:
	#		print col
	#	print row
	#	print '|'.join(row)
#Spam, Spam, Spam, Spam, Spam, Baked Beans
#Spam, Lovely Spam, Wonderful Spam

#words = ['cat', 'window', 'defenestrate']
#for w in words:
#	print w, len(w)

#x = int(raw_input("Please enter an integer: "))
#if x < 0:
#	x = 0
#	print 'Negative changed to zero'
#elif x == 0:
#	print 'Zero'
#elif x == 1:
#	print 'Single'
#else:
#	print 'More'

#fp = Footprint("Name", "Beschreibung", "Tags")
#fp.Render()
#del fp


