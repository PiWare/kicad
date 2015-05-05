LIBRARY_ROOT = library
FOOTPRINT_ROOT = modules

CPU_SCRIPT = script/cpu.py
CAPACITOR_SCRIPT = script/capacitor.py
FOOTPRINT_SCRIPT = script/footprint.py

LIBRARIES = $(LIBRARY_ROOT)/mcu.lib \
			$(LIBRARY_ROOT)/rf.lib \
			$(LIBRARY_ROOT)/capacitor.lib \
			$(FOOTPRINT_ROOT)/dip \
			$(FOOTPRINT_ROOT)/soic \
			$(FOOTPRINT_ROOT)/plcc \

all: $(LIBRARIES)

MCU_CLOCK = data/mcu/pin-table-TM4C123GH6PM.csv\
			data/mcu/stm32F030C8T6RT.csv

$(LIBRARY_ROOT)/mcu.lib: $(CPU_SCRIPT) $(MCU_CLOCK)
	$(CPU_SCRIPT) --clock $(MCU_CLOCK) --output $@

RF_CLOCK = data/rf/cc1121.csv

$(LIBRARY_ROOT)/rf.lib: $(CPU_SCRIPT) $(RF_CLOCK)
	$(CPU_SCRIPT) --clock $(RF_CLOCK) --output $@

CAPACITOR = data/avx_condensator.csv

$(LIBRARY_ROOT)/capacitor.lib: $(CAPACITOR_SCRIPT) $(CAPACITOR)
	$(CAPACITOR_SCRIPT) --data $(CAPACITOR) --output $@


# Footprint generation
FOOTPRINT_DIP  = data/footprint/dip.csv
FOOTPRINT_SOIC = data/footprint/soic.csv
FOOTPRINT_PLCC = data/footprint/plcc.csv

$(FOOTPRINT_ROOT)/dip: $(FOOTPRINT_SCRIPT) $(FOOTPRINT_DIP)
	mkdir -p $@
	$(FOOTPRINT_SCRIPT) --csv $(FOOTPRINT_DIP) --output_path $@

$(FOOTPRINT_ROOT)/soic: $(FOOTPRINT_SCRIPT) $(FOOTPRINT_SOIC)
	mkdir -p $@
	$(FOOTPRINT_SCRIPT) --csv $(FOOTPRINT_SOIC) --output_path $@

$(FOOTPRINT_ROOT)/plcc: $(FOOTPRINT_SCRIPT) $(FOOTPRINT_PLCC)
	mkdir -p $@
	$(FOOTPRINT_SCRIPT) --csv $(FOOTPRINT_PLCC) --output_path $@
