# -*- makefile -*-
CD = cd ${CURDIR}

.DEFAULT_GOAL := install
.PHONY: all

all: clean install test

clean:
	$(CD) && rm -rf build dist sweetpotato.egg-info

install:
	$(CD) && ./setup.py install --force --optimize 2 --user

test:
	$(CD) && ./tests.py
