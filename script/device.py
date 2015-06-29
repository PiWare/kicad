#!/usr/bin/python

import os
import sys
import symbol
from symbol import cfg
import csv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Symbol generator from csv table.')
    parser.add_argument('--csv', type = str, help = 'CSV formatted input table', required = True)
    parser.add_argument('--symbol', type = str, help = 'Output file for generated KiCAD symbols', required = True)
    parser.add_argument('--desc', type = str, help = 'Output file for generated KiCAD symbol description', required = True)
    parser.add_argument('--template_path', type = str, help = 'Path to template symbols', required = True)
    parser.add_argument('--table_path', type = str, help = 'Path to table based symbols', required = True)
    args = parser.parse_args()

    symbol_output = open(args.symbol, "w")
    symbol_output.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
    desc_output = open(args.desc, "w")
    desc_output.write('EESchema-DOCLIB Version 2.0\n')

    args.template_path = os.path.normpath(args.template_path)
    args.table_path = os.path.normpath(args.table_path)

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
                template_file = os.path.join(args.template_path, data['symbol'] + cfg.SYMBOL_TEMPLATE_EXTENSION)
                del data['symbol']

                if not os.path.isfile(template_file):
                    print "Template file '%s' does not exist!"%(template_file)
                    sys.exit(2)

                if last_name != data['name']:
                    if 'sym' in locals():
                        sym.optimize()
                        symbol_output.write("\n".join(sym.renderSymbol()))
                        desc_output.write("\n".join(sym.renderDescription()))
                        del sym

                    firstElement = True
                    sym = symbol.Symbol()
                    last_name = data['name']

                # As many symbols can contain field elements, we load them only from the first symbol
                if not 'unit' in data:
                    data['unit'] = 0
                #print data
                print template_file
                sym.load(template_file, int(data['unit']), symbol.representation.normal, data, firstElement)
                if firstElement:
                    if not sym.setFields(data):
                        print "Error in ", template_file
                        sys.exit(2)
                    sym.setDescriptions(data)
                    firstElement = False

    if 'sym' in locals():
        sym.optimize()
        symbol_output.write("\n".join(sym.renderSymbol()))
        desc_output.write("\n".join(sym.renderDescription()))
        del sym
    symbol_output.write("#\n# End Library\n")
    desc_output.write("#\n# End Doc Library\n")

#sym = symbol.Symbol()
#sym.load("data/template/test.lib")
#print sym.render_()
