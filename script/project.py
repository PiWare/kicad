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
import argparse
import datetime
import locale

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Project file generation.')
    parser.add_argument('--template', metavar = 'template', type = str, help = 'Project template input file', required = True)
    parser.add_argument('--project', metavar = 'project', type = str, help = 'Output project file', required = True)
    parser.add_argument('--symbol_path', metavar = 'symbol_path', type = str, help = 'Symbol path', required = True)
    parser.add_argument('--footprint_path', metavar = 'footprint_path', type = str, help = 'Footprint path', required = True)
    args = parser.parse_args()

    kicad_user = os.path.join(os.path.expanduser("~"), 'kicad')
    if kicad_user != os.getcwd():
        print "WARNING: Library is not in searchpath of KiCAD '%s'. Templates do not work!"%(kicad_user)

    file = open(args.template, "r")
    data = file.read()
    file.close()

    args.symbol_path = os.path.abspath(args.symbol_path)
    args.footprint_path = os.path.abspath(args.footprint_path)

    # KiCAD project file is in INI format, but the first section is missing!
    data = '[hidden]\n' + data
    buffer = StringIO.StringIO(data)
    project = ConfigParser.RawConfigParser()
    project.readfp(buffer)
    buffer.close()

    # Update timestamp
    project.set('hidden', 'update', datetime.datetime.today().strftime("%a %d %b %Y %H:%M:%S %Z"))

    #print project.get('general', 'version')
    #print project.sections()

    # Symbol libs
    project.remove_section('eeschema/libraries')
    project.add_section('eeschema/libraries')
    project.set('eeschema', 'libdir', args.symbol_path)

    libs = []
    for file in os.listdir(args.symbol_path):
        if os.path.isfile(os.path.join(args.symbol_path, file)) and file.endswith(".lib"):
            libs.append(os.path.splitext(file)[0])
    libs.sort()

    index = 1
    for lib in libs:
        project.set('eeschema/libraries', 'LibName'+str(index), lib)
        index += 1

    # Footprint libs
    project.remove_section('pcbnew/libraries')
    project.add_section('pcbnew/libraries')
    project.set('pcbnew/libraries', 'libdir', args.footprint_path)

    libs = []
    for file in os.listdir(args.footprint_path):
        if os.path.isdir(os.path.join(args.footprint_path, file)):
            libs.append(file)
    libs.sort()

    index = 1
    for lib in libs:
        project.set('pcbnew/libraries', 'LibName'+str(index), lib)
        index += 1

    # Serialize INI data and strip of [hidden] section
    buffer = StringIO.StringIO()
    project.write(buffer)
    data = buffer.getvalue()
    data = data.replace("[hidden]\n", "")

    file = open(args.project, "w")
    file.write(data)
    file.close()
