#!/bin/bash

. ../config
. tools.sh

# Generate CSV resistor table


FOOTPRINT=("chip_resistor_0201" "chip_resistor_0402" "chip_resistor_0603" "chip_resistor_0805" "chip_resistor_1206" "chip_resistor_1210" "wire_10mm" "melf" "melf_mini" "melf_micro")
FOOTPRINT_POWER=("0.05" "0.063" "0.1" "0.125" "0.25" "0.5" "0.25" "1" "0.4" "0.3")

DECADE_FIRST=0
DECADE_LAST=7

echo "Generate resistor table"

OUTFILE="resistor.csv"

echo "name,reference,value,tolerance,power,footprint" > $OUTFILE

# Generate E24 and E96
footprint_index=0
while [ $footprint_index -lt "${#FOOTPRINT[@]}" ]
do
	decade=$DECADE_FIRST
	while [ $decade -lt $DECADE_LAST ]
	do
		index=0
		while [ $index -lt ${EROW[$E24]} ]
		do
			value=$(resistor $E24 $decade $index)
			echo "${FOOTPRINT[$footprint_index]}_E24_$value_${TOLERANCE[$E24]}%,R,$value,${TOLERANCE[$E24]}%,${FOOTPRINT_POWER[$footprint_index]}W,${FOOTPRINT[$footprint_index]}" >> $OUTFILE
			index=$((index+1))
		done

	#	index=0
	#	while [ $index -lt ${EROW[$E96]} ]
	#	do
	#		value=$(resistor $E96 $decade $index)
	#		echo "$value,"  #>> $TMPFILE
	#		index=$((index+1))
	#	done
		decade=$((decade+1))
	done
	value=$(resistor $E24 $DECADE_LAST 0)
	echo "${FOOTPRINT[$footprint_index]}_E24_$value_${TOLERANCE[$E24]}%,R,$value,${TOLERANCE[$E24]}%,${FOOTPRINT_POWER[$footprint_index]}W,${FOOTPRINT[$footprint_index]}" >> $OUTFILE

	footprint_index=$((footprint_index+1))
done

