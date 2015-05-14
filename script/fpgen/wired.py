import fp

class wired(fp.base):
	"""Generator for wired resistors, capacitors, ..."""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, count, drill):
		super(fp.base, self).__init__(name, description, tags)
