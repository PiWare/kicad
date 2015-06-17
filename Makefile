LIBRARY_ROOT = library
FOOTPRINT_ROOT = modules

COMMON_SCRIPT_DEPS = script/config.py script/symbol.py config
CPU_SCRIPT = script/cpu.py

CAPACITOR_SCRIPT = script/capacitor.py
DEVICE_SCRIPT = script/device.py
FOOTPRINT_SCRIPT = script/footprint.py
SUMMARY_SCRIPT = script/summary.py
README_SCRIPT = script/readme.py

# Generator based symbols
LIBRARIES = $(LIBRARY_ROOT)/mcu.lib \
			$(LIBRARY_ROOT)/rf.lib \
			$(LIBRARY_ROOT)/capacitor.lib

# Template based symbols
TEMPLATE_LIBRARIES = $(LIBRARY_ROOT)/supply.lib
DEVICES = $(LIBRARY_ROOT)/led.lib

FOOTPRINTS = dip \
	soic \
	plcc \
	pqfp \
	sqfp

all: $(FOOTPRINTS) $(LIBRARIES) $(TEMPLATE_LIBRARIES) $(DEVICES) summary.txt README.md

MCU_CLOCK = data/mcu/pin-table-TM4C123GH6PM.csv\
			data/mcu/stm32F030C8T6RT.csv

$(LIBRARY_ROOT)/mcu.lib: $(CPU_SCRIPT) $(COMMON_SCRIPT_DEPS) $(MCU_CLOCK)
	$(CPU_SCRIPT) --clock $(MCU_CLOCK) --output $@

RF_CLOCK = data/rf/cc1121.csv data/rf/si4468.csv

$(LIBRARY_ROOT)/rf.lib: $(CPU_SCRIPT) $(COMMON_SCRIPT_DEPS) $(RF_CLOCK)
	$(CPU_SCRIPT) --clock $(RF_CLOCK) --output $@

CAPACITOR = data/avx_condensator.csv

$(LIBRARY_ROOT)/capacitor.lib: $(CAPACITOR_SCRIPT) $(COMMON_SCRIPT_DEPS) $(CAPACITOR)
	$(CAPACITOR_SCRIPT) --data $(CAPACITOR) --output $@

SUPPLY = data/device/supply.csv

$(LIBRARY_ROOT)/supply.lib: $(DEVICE_SCRIPT) $(COMMON_SCRIPT_DEPS) $(SUPPLY)
	$(DEVICE_SCRIPT) --csv $(SUPPLY) --symbol $@ --desc $(addsuffix .dcm, $(basename $@))

DEVICE_CSV = data/device/led.csv

$(DEVICES): $(DEVICE_SCRIPT) $(COMMON_SCRIPT_DEPS) $(DEVICE_CSV)
	$(DEVICE_SCRIPT) --csv $(DEVICE_CSV) --symbol $@ --desc $(addsuffix .dcm, $(basename $@))


# Footprint generation
$(FOOTPRINTS): %: data/footprint/%.csv
	mkdir -p $(FOOTPRINT_ROOT)/$@
	$(FOOTPRINT_SCRIPT) --csv $< --output_path $(FOOTPRINT_ROOT)/$@

summary.txt: $(FOOTPRINTS) $(LIBRARIES)
	$(SUMMARY_SCRIPT) --libs $(LIBRARIES) --footprints $(FOOTPRINTS) --output $@

README.md: config
	$(README_SCRIPT) --output $@
