INSTALL_TARGET_DIR = /opt
PYTHON = python3
COPY = /bin/cp -fr ../sweetpotato $(INSTALL_TARGET_DIR)/
REMOVE = /bin/rm -fr $(INSTALL_TARGET_DIR)/sweetpotato /usr/bin/sweetpotato
SYMLINK = ln -s $(INSTALL_TARGET_DIR)/sweetpotato/sweetpotato.py /usr/bin/sweetpotato
TEST = $(PYTHON) tests.py


install:
	$(COPY) && $(SYMLINK)

reinstall:
	$(REMOVE) && $(COPY) && $(SYMLINK)

test:
	$(TEST)

uninstall:
	$(REMOVE)
