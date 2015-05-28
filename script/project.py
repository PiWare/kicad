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
# Generate footprint files from csv table

import os
import ConfigParser
import StringIO

if __name__ == "__main__":
  # parser = argparse.ArgumentParser(description = 'Footprint generator from csv table.')
  # parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
  # parser.add_argument('--output_path', metavar = 'output_path', type = str, help = 'Output path for generated KiCAD footprint files', required = True)
  # args = parser.parse_args()

    file = open('library.pro', "r")
    data  = file.read()
    file.close()

    data = '[hidden]\n' + data
    buffer = StringIO.StringIO(data)
    project = ConfigParser.RawConfigParser()
    project.readfp(buffer)
    print project.get('general', 'version')
    print project.sections()

    project.remove_section('eeschema/libraries')
    project.add_section('eeschema/libraries')

    index = 1
    for file in os.listdir("library"):
        if file.endswith(".lib"):
            project.set('eeschema/libraries', 'LibName'+str(index), os.path.splitext(file)[0])
            index += 1

    project.write(buffer)
    print buffer.getvalue()
