#!/usr/bin/python

# http://www.nxp.com/technical-support-portal/#/tid=50808,tab=datasheets

import symbol
from symbol import cfg
import csv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Symbol generator from csv table.')
    parser.add_argument('--csv', type = str, help = 'CSV formatted input table', required = True)
    parser.add_argument('--symbol', type = str, help = 'KiCAD output symbol file', required = True)
    args = parser.parse_args()

#   symbol_output = open(args.symbol, "w")
#   symbol_output.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
#   desc_output = open(args.desc, "w")
#   desc_output.write('EESchema-DOCLIB Version 2.0\n')

    sym = symbol.Symbol()
    sym.fromCSV(args.csv, "TEST", "IC", 50, True, True, False)
    sym.optimize()

    with open(args.symbol, 'w') as symbol_output:
        symbol_output.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
        symbol_output.write("\n".join(sym.renderSymbol()))
        symbol_output.close()

#   symbol_output.write("#\n# End Library\n")
#   desc_output.write("#\n# End Doc Library\n")
