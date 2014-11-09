help:
	@echo "Help:"
	@echo ""
	@echo "* prepare: will convert Readme.md file into .rst"
	@echo ""
	@echo ""

prepare:
	pandoc -f markdown -t rst README.md > README.rst
