#!/bin/bash

function symlib_start() {
	echo "EESchema-LIBRARY Version 2.3"
	echo "#encoding utf-8"
}

# Create symbol entry
# $1 - 
#
#
function symlib_symbol() {
	echo ""
}

function symlib_end() {
	echo "#"
	echo "#End Library"
}

# Resistor

E3=0
E6=1
E12=2
E24=3
E48=4
E96=5
E192=6

# E3, E6, E12, E24, E48, E96, E192
TOLERANCE=(20 20 10 5 2 1 0.5)
EROW=(3 6 12 24 48 96 192)
PRECISION=(1 1 1 1 2 2 2)
DECIMAL_CHAR=("R" "R" "R" "k" "k" "k" "M" "M" "M")

# resistor(EROW_INDEX, DECADE, INDEX)
function resistor() {
	local DECADE=$2
	local DECADE_MOD=$((DECADE % 3))
	local INDEX=$3
	local RESULT=$(gawk "BEGIN { printf(\"%.${PRECISION[$1]}f\n\", (10^(1/${EROW[$1]}))^$INDEX ) }")

	# Fix rounding problem in E3, E6, E12 and E24 row
	if [ ${EROW[$1]} -le 24 ]
	then
		RESULT=$(gawk "BEGIN { printf(\"%.0f\n\", $RESULT * 10 ) }")
		if [ $RESULT -ge 26 ] && [ $RESULT -le 46 ]
		then
			RESULT=$((RESULT + 1))
		else
			if [ $RESULT -eq 83 ]
			then
				RESULT=$((RESULT - 1))
			fi
		fi
		RESULT=$(gawk "BEGIN { printf(\"%.${PRECISION[$1]}f\n\", $RESULT / 10 ) }")
	fi

	RESULT=$(gawk "BEGIN { printf(\"%.4g\n\", $RESULT*10^$DECADE_MOD ) }")
	if [ $(expr index "$RESULT" .) -eq 0 ]
	then
		echo $RESULT${DECIMAL_CHAR[$DECADE]}
	else
		echo ${RESULT/./${DECIMAL_CHAR[$DECADE]}}
	fi
}

# Footprint
INCH="25.4"

# Chip
# footprint_chip($NAME, $PART_WIDTH, $PART_HEIGHT, $PAD_WIDTH, $PAD_HEIGHT, $PAD_DISTANCE)
function footprint_chip() {
	local NAME="$1"
	local PACKAGE_WIDTH="$2"
	local PACKAGE_HEIGHT="$3"
	local PAD_WIDTH="$4"
	local PAD_HEIGHT="$5"
	local PAD_DISTANCE="$6"
	local PACKAGE_3D="$7"

#	echo $NAME $PACKAGE_WIDTH $PACKAGE_HEIGHT $PAD_WIDTH $PAD_HEIGHT $PAD_DISTANCE

	PACKAGE_WIDTH_HALF=$(gawk "BEGIN { printf(\"%.${FOOTPRINT_PRECISION}f\n\", $PACKAGE_WIDTH / 2 ) }")
	PACKAGE_HEIGHT_HALF=$(gawk "BEGIN { printf(\"%.${FOOTPRINT_PRECISION}f\n\", $PACKAGE_HEIGHT / 2 ) }")
	PAD_DISTANCE_HALF=$(gawk "BEGIN { printf(\"%.${FOOTPRINT_PRECISION}f\n\", $PAD_DISTANCE / 2 ) }")

	echo "(module $NAME (tedit $FOOTPRINT_TIMESTAMP)"
	echo "  (attr smd)"

#	if (vm.count("description"))
#	{
#		cout << "  (descr \"" << description << "\")" << endl;
#	}

#	if (vm.count("tags"))
#	{
#		cout << "  (tags \"" << tags << "\")" << endl;
#	}

	echo "  (fp_text reference REF** (at 0 0.5) (layer F.SilkS)"
	echo "    (effects (font (size $FOOTPRINT_FONT_SIZE $FOOTPRINT_FONT_SIZE) (thickness $FOOTPRINT_FONT_THICKNESS)))"
	echo "  )"

	echo "  (fp_text value VAL** (at 0 -0.5) (layer F.Fab)"
	echo "    (effects (font (size $FOOTPRINT_FONT_SIZE $FOOTPRINT_FONT_SIZE) (thickness $FOOTPRINT_FONT_THICKNESS)))"
	echo "  )"

	# Package outline
	echo "  (fp_line (start -$PACKAGE_WIDTH_HALF -$PACKAGE_HEIGHT_HALF) (end  $PACKAGE_WIDTH_HALF -$PACKAGE_HEIGHT_HALF) (layer F.SilkS) (width $FOOTPRINT_LINE_WIDTH))"
	echo "  (fp_line (start  $PACKAGE_WIDTH_HALF -$PACKAGE_HEIGHT_HALF) (end  $PACKAGE_WIDTH_HALF  $PACKAGE_HEIGHT_HALF) (layer F.SilkS) (width $FOOTPRINT_LINE_WIDTH))"
	echo "  (fp_line (start  $PACKAGE_WIDTH_HALF  $PACKAGE_HEIGHT_HALF) (end -$PACKAGE_WIDTH_HALF  $PACKAGE_HEIGHT_HALF) (layer F.SilkS) (width $FOOTPRINT_LINE_WIDTH))"
	echo "  (fp_line (start -$PACKAGE_WIDTH_HALF  $PACKAGE_HEIGHT_HALF) (end -$PACKAGE_WIDTH_HALF -$PACKAGE_HEIGHT_HALF) (layer F.SilkS) (width $FOOTPRINT_LINE_WIDTH))"

	# Pins
	echo "  (pad 1 smd rect (at -$PAD_DISTANCE_HALF 0) (size $PAD_WIDTH $PAD_HEIGHT) (layers F.Cu F.Paste F.Mask))"
	echo "  (pad 2 smd rect (at  $PAD_DISTANCE_HALF 0) (size $PAD_WIDTH $PAD_HEIGHT) (layers F.Cu F.Paste F.Mask))"

	# 3D package
	if [ -n "$PACKAGE_3D" ]
	then
		echo "PACKAGE"
	fi

	echo ")"
}

# SOIC
function footprint_soic() {
	local NAME="$1"
	local PACKAGE_3D="$2"
	local PACKAGE_WIDTH="$3"
	local PACKAGE_HEIGHT="$4"
	local PAD_WIDTH="$5"
	local PAD_HEIGHT="$6"
	local PAD_DISTANCE="$7"
	local DESCRIPTION="$8"

}

# Dual inline
function footprint_dil() {
	local NAME="$1"
	local PACKAGE_3D="$2"
	local PACKAGE_WIDTH="$3"
	local PACKAGE_HEIGHT="$4"
	local PAD_HOLE="$5"
#	local PAD_DIAMETER="$6"
	local PAD_WIDTH="$5"
	local PAD_HEIGHT="$6"
	local PAD_DISTANCE="$7"
	local DESCRIPTION="$8"

}

# Pin lines? Generate as DIL?

# Wired parts with 2 pins (resistors, diodes)
function footprint_wired() {
	local NAME="$1"
	local PACKAGE_3D="$2"
	local PACKAGE_WIDTH="$3"
	local PACKAGE_HEIGHT="$4"
	local PAD_HOLE="$5"
	local PAD_DIAMETER="$6"
#	local PAD_WIDTH="$5"
#	local PAD_HEIGHT="$6"
	local PAD_DISTANCE="$7"
	local DESCRIPTION="$8"

}

