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
#
# Generate readme.md file containing library configuration

import config

cfg = config.Config("config")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate a readme file in markdown syntac containing library configuration.')
    parser.add_argument('--output', metavar = 'out', type = str, help = 'Output file', required = True)
    args = parser.parse_args()

    output = open(args.output, "w")
    output.write("""# kicad
KiCad library used in our projects. Main parts are generated using python scripts and input data from csv tables. This should give a very flexible base to add new symbols, footprings and parts.

All dimension are in millimeters/degree, if not otherwise noted.

## Naming conventions

- Filenames are lowercase and separated with underscore (e.g. resistor_1k5_chip_0805, dip_8_narrow)
- Devicesnames are uppercase and separated with underscore (e.g. SOIC_8_WIDE, 74HC595)

""")

    output.write("## Symbol\n")

    output.write("\n### Configuration\n\n")

    output.write("F#-Field usage:\n")
    # This entries are reverse, so we make a little map
    map = {}
    for value in cfg.dict():
        part = value.split("_", 1)
        if len(part) == 2 and part[1] == 'FIELD':
            map[int(getattr(cfg, value))] = getattr(cfg, part[0]+"_NAME")

    for key in sorted(map):
        output.write("* **F%d**: %s\n"%(key, map[key]))

    map = {}
    for value in cfg.dict():
        part = value.split("_", 1)
        if len(part) == 2 and part[0] == 'SYMBOL':
            map[value] = getattr(cfg, value)

    for key in sorted(map):
        output.write("* **%s**: %s\n"%(key, map[key]))

    output.write("\n### Generators\n\n")

    output.write("\n## Footprint\n\n")

    output.write("\n### Configuration\n\n")

    map = {}
    for value in cfg.dict():
        part = value.split("_", 1)
        if len(part) == 2 and part[0] == 'FOOTPRINT':
            map[value] = getattr(cfg, value)

    for key in sorted(map):
        output.write("* **%s**: %s\n"%(key, map[key]))

    output.write("\n### Generators\n\n")

    output.close()
