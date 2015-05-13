import time
import config
cfg = config.Config("config")

registered_footprints = {}

class metaclass_register(type):
	def __init__(self, name, bases, nmspc):
		super(metaclass_register, self).__init__(name, bases, nmspc)
		registered_footprints[name] = self

class footprint(object):
#	__metaclass__ = metaclass_register

	def __init__(self, name, description = "", tags = "", smd = False, add_text = True):
		self.name = name
		self.description = description
		self.tags = tags
		self.smd = smd
		self.elements = []

		if add_text:
			self.elements.append(fp.text(cfg.FOOTPRINT_REFERENCE_LAYER, "reference", "REF**", 0, 0, cfg.FOOTPRINT_REFERENCE_FONT_SIZE, cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS))
			self.elements.append(fp.text(cfg.FOOTPRINT_VALUE_LAYER, "value", "VAL**", 0, cfg.FOOTPRINT_VALUE_FONT_SIZE + 2 * cfg.FOOTPRINT_VALUE_FONT_THICKNESS, cfg.FOOTPRINT_VALUE_FONT_SIZE, cfg.FOOTPRINT_VALUE_FONT_THICKNESS))

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
		result += ')\n'
		return result
