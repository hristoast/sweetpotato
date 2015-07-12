# -*- makefile -*-
BDIST = ./setup.py bdist
BUILD = ./setup.py build --force
CLEAN = /bin/rm -fr MANIFEST build dist *.egg-info sweetpotato/__pycache__
CLEAN2 = find . -type f -name "*~" -exec /bin/rm -f {} \;
CLEAN_TEST = /bin/rm -fr /tmp/_sp_test*
DESTDIR = bin
PREFIX = /usr/local
INSTALL = ./setup.py install --force --optimize 2
SDIST = ./setup.py sdist
TEST = ./tests.py
UNINSTALL = /bin/rm -rf $(PREFIX)/lib/python3*/dist-packages/sweetpotato* \
	$(PREFIX)/bin/sweetpotato*
UNINSTALL_PYENV = \
	/bin/rm -rf "~/.pyenv/versions/3*/lib/python3*/site-packages/sweetpotato*" \
	~/.pyenv/shims/sweetpotato ~/.pyenv/shims/sweetpotatod

.DEFAULT_GOAL := sdist
.PHONY: all

all: bdist build clean cleantest full_uninstall install i reinstall sdist \
	 test uninstall uninstall_pyenv

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

full_uninstall:
	$(UNINSTALL) && $(UNINSTALL_PYENV)

install:
	$(INSTALL)

i:
	$(INSTALL) && $(CLEAN)

reinstall:
	$(INSTALL)

sdist:
	$(SDIST)

test:
	$(TEST)

uninstall:
	$(UNINSTALL)

uninstall_pyenv:
	$(UNINSTALL_PYENV)
