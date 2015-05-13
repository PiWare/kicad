import footprint

class wired(footprint):
	"""Generator for wired resistors, capacitors, ..."""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, count, drill):
		footprint.__init__(self, name, description, tags)
