LIBRARY_ROOT = library

CPU_SCRIPT = script/cpu.py

LIBRARIES = $(LIBRARY_ROOT)/mcu.lib \
			$(LIBRARY_ROOT)/rf.lib

all: $(LIBRARIES)

MCU_CLOCK = data/mcu/pin-table-TM4C123GH6PM.csv\
			data/mcu/stm32F030C8T6RT.csv

$(LIBRARY_ROOT)/mcu.lib: $(CPU_SCRIPT) $(MCU_CLOCK)
	$(CPU_SCRIPT) --clock $(MCU_CLOCK) --output $@

RF_CLOCK = data/rf/cc1121.csv

$(LIBRARY_ROOT)/rf.lib: $(CPU_SCRIPT) $(RF_CLOCK)
	$(CPU_SCRIPT) --clock $(RF_CLOCK) --output $@
