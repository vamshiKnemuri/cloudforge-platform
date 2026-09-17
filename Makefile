.PHONY: test run validate package

PYTHON ?= python3

test:
	$(PYTHON) -m unittest discover -s app/tests -v

run:
	$(PYTHON) app/server.py

validate:
	$(PYTHON) scripts/validate_project.py

package:
	tar --exclude='.git' --exclude='.terraform' -czf cloudforge-platform.tar.gz .

