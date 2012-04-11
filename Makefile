DUMPER = ./dumper.py

.PHONY: web/ways.json

web/ways.json:
	$(DUMPER) railways roadways area population 'GDP - per capita (PPP)=percapita' > $@
