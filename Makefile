LIBRARY_ROOT = library
FOOTPRINT_ROOT = modules
CSV_ROOT := data/device
TEMPLATE_ROOT := data/template
TABLE_ROOT := data/symbol

COMMON_SCRIPT_DEPS = script/config.py script/symbol.py config
DEVICE_SCRIPT = script/device.py
FOOTPRINT_SCRIPT = script/footprint.py
SUMMARY_SCRIPT = script/summary.py
README_SCRIPT = script/readme.py
PROJECT_SCRIPT = script/project.py

RESISTOR_SCRIPT := script/devgen/resistor.py

# Template/table based symbols
TEMPLATE_LIBRARIES := $(LIBRARY_ROOT)/supply.lib \
	$(LIBRARY_ROOT)/led.lib \
	$(LIBRARY_ROOT)/transistor.lib \
	$(LIBRARY_ROOT)/logic.lib \
	$(LIBRARY_ROOT)/diode.lib \
	$(LIBRARY_ROOT)/driver.lib \
	$(LIBRARY_ROOT)/connector.lib \
	$(LIBRARY_ROOT)/mcu.lib \
	$(LIBRARY_ROOT)/resistor.lib \
	$(LIBRARY_ROOT)/inductor.lib \
	$(LIBRARY_ROOT)/capacitor.lib \
	$(LIBRARY_ROOT)/rf.lib 


TEMPLATE_LIBRARIES_CSV := $(patsubst $(LIBRARY_ROOT)/%.lib, $(CSV_ROOT)/%.csv, $(TEMPLATE_LIBRARIES))

# Footprints
FOOTPRINTS = dip \
	soic \
	plcc \
	pqfp \
	sqfp

# Project files/templates
PROJECTS = library.pro \
	template/kicad.pro \
	template/basic/basic.pro \
	template/phoenix_me_tbus/phoenix_me_tbus.pro

all: $(FOOTPRINTS) $(LIBRARIES) $(TEMPLATE_LIBRARIES) $(PROJECTS) summary.txt README.md

# Resistor
RESISTOR_TABLE := data/device/resistor.csv
$(RESISTOR_TABLE): $(RESISTOR_SCRIPT)
	$(RESISTOR_SCRIPT) --erow 24 96 --footprint chip_resistor_0201 chip_resistor_0402 chip_resistor_0603 chip_resistor_0805 chip_resistor_1206 chip_resistor_1210 wire_10mm melf melf_mini melf_micro --output_file $@

# Template based symbols
$(LIBRARY_ROOT)/%.lib: $(CSV_ROOT)/%.csv $(DEVICE_SCRIPT) $(COMMON_SCRIPT_DEPS)
	$(DEVICE_SCRIPT) --csv $< --symbol $@ --desc $(addsuffix .dcm, $(basename $@)) --template_path $(TEMPLATE_ROOT)/ --table_path $(TABLE_ROOT)/

# Footprint generation
$(FOOTPRINTS): %: data/footprint/%.csv
	mkdir -p $(FOOTPRINT_ROOT)/$@
	$(FOOTPRINT_SCRIPT) --csv $< --output_path $(FOOTPRINT_ROOT)/$@

summary.txt: $(FOOTPRINTS) $(TEMPLATE_LIBRARIES)
	$(SUMMARY_SCRIPT) --libs $(TEMPLATE_LIBRARIES) --footprints $(FOOTPRINTS) --output $@

# Uncomment dependency on $(FOOTPRINTS), when it works!
#library.pro: $(FOOTPRINTS) $(TEMPLATE_LIBRARIES)
$(PROJECTS): $(TEMPLATE_LIBRARIES)
	$(PROJECT_SCRIPT) --template data/project.pro --symbol_path $(LIBRARY_ROOT) --footprint_path $(FOOTPRINT_ROOT) --project $@

README.md: config
	$(README_SCRIPT) --output $@
