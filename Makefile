BDIST = python3 setup.py bdist
BUILD = python3 setup.py build --force
CLEAN = /bin/rm -fr MANIFEST build dist *.egg-info sweetpotato/__pycache__
CLEAN2 = find . -type f -name "*~" -exec /bin/rm -f {} \;
CLEAN_TEST = /bin/rm -fr /tmp/_sp_test*
INSTALL = python3 setup.py install --force --optimize 2
SDIST = python3 setup.py sdist
TEST = ./tests.py
UNINSTALL = /bin/rm -rf /usr/local/lib/python3*/dist-packages/sweetpotato*

.DEFAULT_GOAL := sdist
.PHONY: all

all: bdist build clean cleantest install i reinstall sdist test

# sweetpotato won't actually work out of a bdist ...
bdist:
	$(BDIST)

# or a build..
build:
	$(BUILD)

clean:
	$(CLEAN) && $(CLEAN2)

cleantest:
	$(CLEAN_TEST)

install:
	$(INSTALL)

i:
	$(INSTALL) && $(CLEAN)

sdist:
	$(SDIST)

reinstall:
	$(INSTALL)

test:
	$(TEST)

uninstall:
	$(UNINSTALL)
