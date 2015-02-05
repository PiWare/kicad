#!/bin/bash

supply_ground=(GND AGND DGND VSS)
supply_positive=(+1V2 +1V5 +1V8 +2V5 +3V3 +5V +12V +24V)
supply_negative=(-3V3 -5V -12V)

ground_type1=()
ground_type2=()
ground_type3=()

echo "EESchema-LIBRARY Version 2.3"
echo "#encoding utf-8"

for name in ${supply_ground[*]}
do
	sed "s/NAME/$name/g" supply_ground.dummy
done

for name in ${supply_positive[*]}
do
	sed "s/NAME/$name/g" supply_positive.dummy
done

for name in ${supply_negative[*]}
do
	sed "s/NAME/$name/g" supply_negative.dummy
done

echo "#"
echo "#End Library"

