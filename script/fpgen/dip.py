import fp
import config
cfg = config.Config("config")

class dip(fp.base):
	"""Generator for dual inline ICs"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, pad_count, pad_drill):
		super(dip, self).__init__(name, description, tags)

		if pad_count % 2:
			raise NameError("pad_count is odd")

		pin = 1
		x = pad_grid * -((float(pad_count) / 4) - 0.5)
		line_x = package_width / 2

		fp.base.add(self, fp.rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))
		fp.base.add(self, fp.arc(cfg.FOOTPRINT_PACKAGE_LAYER, -line_x, 0, -line_x, 1.0, -180, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))
		for i in range(pad_count / 2):
			fp.base.add(self, fp.pad(cfg.FOOTPRINT_THD_LAYERS, pin, fp.technology.thru_hole, fp.type.oval, x, pad_distance / 2, pad_width, pad_height, pad_drill))
			x += pad_grid
			pin += 1

		for i in range(pad_count / 2, pad_count):
			x -= pad_grid
			fp.base.add(self, fp.pad(cfg.FOOTPRINT_THD_LAYERS, pin, fp.technology.thru_hole, fp.type.oval, x, -pad_distance / 2, pad_width, pad_height, pad_drill))
			pin += 1
