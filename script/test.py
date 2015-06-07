#!/usr/bin/python

import os
import symbol
from symbol import cfg
import csv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Symbol generator from csv table.')
    parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
#   parser.add_argument('--output_path', metavar = 'output_path', type = str, help = 'Output path for generated KiCAD footprint files', required = True)
    args = parser.parse_args()

    with open(args.csv, 'rb') as csvfile:
        table = csv.reader(csvfile, delimiter=',', quotechar='\"')

        last_name = ""
        first_row = 1
        for row in table:
            if first_row == 1:
                header = row
                first_row = 0
            else:
                data = dict(zip(header, row))
                # Can this be made little bit more elegant?
                for key in data:
                    try:
                    #   if key.find("count") != -1:
                    #       data[key] = int(data[key])
                    #   else:
                        data[key] = int(data[key])
                    except:
                        pass

                template_file = cfg.SYMBOL_TEMPLATE_PATH + data['symbol'] + cfg.SYMBOL_TEMPLATE_EXTENSION
                del data['symbol']

                if os.path.isfile(template_file):
                    print template_file

                if last_name != data['name']:
                    if 'sym' in locals():
                        sym.render_()
                        del sym

                    sym = symbol.Symbol()

                    print "New symbol "+data['name']
                    last_name = data['name']

                print "Add unit %d"%(data['unit'])
                sym.load(template_file, data['unit'])
    print "Finish last symbol"

#sym = symbol.Symbol()
#sym.load("data/template/test.lib")
#print sym.render_()
