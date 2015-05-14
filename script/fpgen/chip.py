import fp
from fp import cfg

class chip(fp.base):
	"""Generator for chip resistors, capacitors, inductors, MELF and Tantal devices"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height):
		super(chip, self).__init__(name, description, tags, True)

		self.package_width = package_width
		self.package_height = package_height
		self.pad_width = pad_width
		self.pad_height = pad_height
		fp.base.add(self, fp.rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))

class chip_pol(chip):
	"""Generator for chip devices with polarity marker"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height):
		super(chip_pol, self).__init__(name, description, tags, package_width, package_height, pad_width, pad_height)

		line_x = package_width / 2 + package_widht * 0.1
		line_y = package_height / 2
		fp.base.add(self, fp.line(cfg.FOOTPRINT_PACKAGE_LAYER, -line_x, -line_y, -line_x, line_y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))
