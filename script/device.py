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
                # Check data for every line
                if 'symbol' not in data or 'name' not in data:
                    print "Missing one or more of the required fields 'symbol' and 'name' in CSV data"
                    sys.exit(2)

                # Create file strings
                template_file = os.path.join(args.template_path, data['symbol'] + cfg.SYMBOL_TEMPLATE_EXTENSION)
                table_file = os.path.join(args.table_path, data['symbol'] + cfg.SYMBOL_TABLE_EXTENSION)

                # Name changed, we have to save symbol and create a new one
                if last_name != data['name']:
                    if 'sym' in locals():
                        sym.optimize()
                        symbol_output.write("\n".join(sym.renderSymbol()))
                        desc_output.write("\n".join(sym.renderDescription()))
                        del sym

                    # Simple error checking
                    if 'reference' not in data:
                        print "Missing the required field 'reference' in CSV data"
                        sys.exit(2)

                    # Check optional fields
                    if 'footprint' not in data:
                        data['footprint'] = ''

                    if 'alias' not in data:
                        data['alias'] = ''

                    if 'description' not in data:
                        data['description'] = ''

                    if 'keywords' not in data:
                        data['keywords'] = ''

                    if 'document' not in data:
                        data['document'] = ''

                    if 'section' not in data:
                        data['section'] = ''

                    firstElement = True
                    sym = symbol.Symbol(data['name'], data['reference'], data['footprint'], data['alias'], data['description'], data['keywords'], data['document'])
                    last_name = data['name']

                if 'unit' not in data:
                    data['unit'] = "0"

                unit = int(data['unit'])
                if os.path.isfile(template_file):
                    sym.load(template_file, unit, symbol.representation.normal, data, firstElement)
                elif os.path.isfile(table_file):
                    sym.fromCSV(table_file, unit, data['section'], unit != 0)
                    #if not unit and 'value' in data:
                    #   sym.addModule(symbol.Text(0, 0, data['value'], cfg.SYMBOL_TEXT_SIZE))

                #elif os.path.isfile(port_table_file):
                #   sym.fromCSV(port_table_file, int(data['unit']), cfg.SYMBOL_PIN_TEXT_OFFSET, False)
                else:
                    print "Template file '%s' or table file '%s' does not exist!"%(template_file, table_file)
                    sys.exit(2)

                # As many symbols can contain field elements, we load them only from the first symbol
                if firstElement:
                    if not sym.setFields(data):
                    #   print "Error in ", template_file
                        print "Error setting fields"
                        sys.exit(2)
                    #sym.setDescriptions(data)
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
