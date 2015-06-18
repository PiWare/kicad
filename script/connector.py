#!/usr/bin/python

# http://www.nxp.com/technical-support-portal/#/tid=50808,tab=datasheets

import os
import sys
#import symbol
#from symbol import cfg
#import csv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Symbol generator from csv table.')
    parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
#   parser.add_argument('--symbol', metavar = 'symbol', type = str, help = 'Output file for generated KiCAD symbols', required = True)
#   parser.add_argument('--desc', metavar = 'desc', type = str, help = 'Output file for generated KiCAD symbol description', required = True)
#   parser.add_argument('--template_path', metavar = 'template_path', type = str, help = 'Path to template symbols', required = True)
    args = parser.parse_args()

#   symbol_output = open(args.symbol, "w")
#   symbol_output.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
#   desc_output = open(args.desc, "w")
#   desc_output.write('EESchema-DOCLIB Version 2.0\n')

    line = ['name', 'number', 'type', 'shape', 'direction']
    result = ";".join(line)+"\n"
    for number in range(10):
        line = ['~', str(number + 1), 'passive', 'line', 'left']
        result += ";".join(line)+"\n"
    print result

