INSTALL_TARGET_DIR = /opt
CLEAN = /bin/rm -rf __pycache__ /tmp/_sp_test*
COPY = /bin/cp -fr ../sweetpotato $(INSTALL_TARGET_DIR)/
REMOVE = /bin/rm -fr $(INSTALL_TARGET_DIR)/sweetpotato /usr/bin/sweetpotato
SYMLINK = ln -s $(INSTALL_TARGET_DIR)/sweetpotato/sweetpotato.py /usr/bin/sweetpotato
TEST = ./tests.py


clean:
	$(CLEAN)

install:
	$(COPY) && $(SYMLINK)

reinstall:
	$(REMOVE) && $(COPY) && $(SYMLINK)

test:
	$(TEST)

uninstall:
	$(REMOVE)
