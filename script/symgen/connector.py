#!/usr/bin/python

# http://www.nxp.com/technical-support-portal/#/tid=50808,tab=datasheets

import os
import csv
import argparse

def PinTable(number, orientation, decoration = ''):
    line = ['name', 'number', 'type', 'shape', 'direction', 'decoration']
    result = ",".join(line)+"\n"
    if (orientation == 'both'):
        if number % 2:
            raise ValueError('If orientation is both, number of pins can not be odd!')

        pin = 1
        for index in range(number / 2):
            line = ['~', str(pin), 'passive', 'line', 'left', decoration]
            result += ",".join(line)+"\n"
            line = ['~', str(pin + 1), 'passive', 'line', 'right', decoration]
            result += ",".join(line)+"\n"
            pin += 2
    else:
        for pin in range(number):
            line = ['~', str(pin + 1), 'passive', 'line', orientation, decoration]
            result += ",".join(line)+"\n"
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Symbol generator from csv table.')
    parser.add_argument('--csv', type = str, help = 'Output file for generated KiCAD symbols', required = True)
    parser.add_argument('--output_path', type = str, help = 'Output file for generated KiCAD symbols', required = True)
#   parser.add_argument('--number', type = int, help = 'Number of pins', required = True)
#   parser.add_argument('--orientation', choices = ['left', 'right', 'both'], help = 'Orientation of pins', required = True)
#   parser.add_argument('--decoration', choices = ['none', 'point', 'square', 'rectangle'], help = 'Decoration of pins', default = 'none')
    args = parser.parse_args()

    with open(args.csv, 'rb') as csvfile:
        table = csv.reader(csvfile, delimiter=',', quotechar='\"')

        first_row = 1
        for row in table:
            if first_row == 1:
                header = row
                first_row = 0
            else:
                for i in range(len(row)):
                    try:
                        row[i] = int(row[i])
                    except:
                        pass

                data = dict(zip(header, row))
                if 'decoration' not in data:
                    data['decoration'] = 'rectangle'

                with open(os.path.join(args.output_path, data['name'] + '.csv'), 'w') as outfile:
                    outfile.write(PinTable(data['number'], data['orientation'], data['decoration']))
                    outfile.close()
