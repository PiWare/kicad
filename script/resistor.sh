#!/bin/bash

NAME="VALUE"
WERT="100k"
VALUE="123"

test=$(head -n -2 "resistor.lib" | tail -n +3 -)
test="${test/\$$NAME/$WERT}"

echo "$test"
echo $((NAME))


test="DRAW\nS -150 50 150 -50 0 1 $SYMBOL_LINE_WIDTH f\nX 1 1 -250 0 $SYMBOL_PIN_LENGTH R $SYMBOL_PIN_NUMBER_SIZE $SYMBOL_PIN_NAME_SIZE 1 1 P\nX 2 2 250 0 $SYMBOL_PIN_LENGTH L $SYMBOL_PIN_NUMBER_SIZE $SYMBOL_PIN_NAME_SIZE 1 1 P\nENDDRAW"

symlib_start
echo $VALUE_FIELD
echo -e $test
symlib_end
