help:
	@echo "Help:"
	@echo ""
	@echo "* checklist: shows the checklist"
	@echo "* prepare: will convert Readme.md file into .rst"
	@echo ""
	@echo ""

checklist:
	@echo "Checklist"
	@echo ""
	@echo " [ ] edit 'meuhdb/__init__.py' to bump version"
	@echo " [ ] edit 'Changelog' to close version"
	@echo " [ ] edit 'README' to make sure the docs are up-to-date"
	@echo " [ ] convert 'README' to rst using 'make prepare'"
	@echo " [ ] python setup.py sdist (check if issues)"
	@echo " [ ] python setup.py sdist upload"
	@echo " [ ] git commit (if needed)"
	@echo " [ ] git tag"
	@echo " [ ] git push --tags"
	@echo " [ ] edit meuhdb/__init__.py and Changelog to upgrade to dev"
	@echo ""

prepare:
	pandoc -f markdown -t rst README.md > README.rst
