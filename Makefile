LIBRARY_ROOT = library
FOOTPRINT_ROOT = modules

COMMON_SCRIPT_DEPS = script/config.py script/symbol.py
CPU_SCRIPT = script/cpu.py
CAPACITOR_SCRIPT = script/capacitor.py
FOOTPRINT_SCRIPT = script/footprint.py

LIBRARIES = $(LIBRARY_ROOT)/mcu.lib \
			$(LIBRARY_ROOT)/rf.lib \
			$(LIBRARY_ROOT)/capacitor.lib

FOOTPRINTS = dip \
	soic \
	plcc \
	pqfp \
	sqfp

all: $(FOOTPRINTS) $(LIBRARIES)

MCU_CLOCK = data/mcu/pin-table-TM4C123GH6PM.csv\
			data/mcu/stm32F030C8T6RT.csv

$(LIBRARY_ROOT)/mcu.lib: $(CPU_SCRIPT) $(COMMON_SCRIPT_DEPS) $(MCU_CLOCK)
	$(CPU_SCRIPT) --clock $(MCU_CLOCK) --output $@

RF_CLOCK = data/rf/cc1121.csv

$(LIBRARY_ROOT)/rf.lib: $(CPU_SCRIPT) $(COMMON_SCRIPT_DEPS) $(RF_CLOCK)
	$(CPU_SCRIPT) --clock $(RF_CLOCK) --output $@

CAPACITOR = data/avx_condensator.csv

$(LIBRARY_ROOT)/capacitor.lib: $(CAPACITOR_SCRIPT) $(COMMON_SCRIPT_DEPS) $(CAPACITOR)
	$(CAPACITOR_SCRIPT) --data $(CAPACITOR) --output $@

# Footprint generation
$(FOOTPRINTS): %: data/footprint/%.csv
	mkdir -p $(FOOTPRINT_ROOT)/$@
	$(FOOTPRINT_SCRIPT) --csv $< --output_path $(FOOTPRINT_ROOT)/$@
