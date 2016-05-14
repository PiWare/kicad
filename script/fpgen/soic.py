import fp
from fp import cfg

class soic(fp.base):
	"""Generator for small outline ICs"""

	def __init__(self, name, model, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, pad_count):
		super(soic, self).__init__(name, model, description, tags, True, False)

		if pad_count % 2:
			raise NameError("pad_count is odd")

		fp.base.add(self, fp.text(cfg.FOOTPRINT_REFERENCE_LAYER, "reference", "REF**", -package_width / 2 - cfg.FOOTPRINT_REFERENCE_FONT_SIZE, 0, 90, cfg.FOOTPRINT_REFERENCE_FONT_SIZE, cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS))
		fp.base.add(self, fp.text(cfg.FOOTPRINT_VALUE_LAYER, "value", "VAL**", 0, 0, 0, cfg.FOOTPRINT_VALUE_FONT_SIZE, cfg.FOOTPRINT_VALUE_FONT_THICKNESS))

		pin = 1
		x = pad_grid * -((float(pad_count) / 4) - 0.5)
		line_x = package_width / 2
		line_y = package_height / 2 - 0.5

		fp.base.add(self, fp.rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))
		fp.base.add(self, fp.line(cfg.FOOTPRINT_PACKAGE_LAYER, -line_x, line_y, line_x, line_y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))

		diff = -line_x - x
		line_y += diff
		fp.base.add(self, fp.circle(cfg.FOOTPRINT_PACKAGE_LAYER, x, line_y, x - 0.3, line_y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))
		for i in range(pad_count / 2):
			fp.base.add(self, fp.pad(cfg.FOOTPRINT_SMD_LAYERS, pin, fp.technology.smd, fp.type.rect, x, pad_distance / 2, pad_width, pad_height))
			x += pad_grid
			pin += 1

		for i in range(pad_count / 2, pad_count):
			x -= pad_grid
			fp.base.add(self, fp.pad(cfg.FOOTPRINT_SMD_LAYERS, pin, fp.technology.smd, fp.type.rect, x, -pad_distance / 2, pad_width, pad_height))
			pin += 1
