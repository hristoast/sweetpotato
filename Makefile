INSTALL_TARGET_DIR = /opt
COPY = /bin/cp -fr ../sweetpotato $(INSTALL_TARGET_DIR)/
REMOVE = /bin/rm -fr $(INSTALL_TARGET_DIR)/sweetpotato /usr/bin/sweetpotato
SYMLINK = ln -s $(INSTALL_TARGET_DIR)/sweetpotato/sweetpotato.py /usr/bin/sweetpotato


install:
	$(COPY) && $(SYMLINK)

reinstall:
	$(REMOVE) && $(COPY) && $(SYMLINK)

uninstall:
	$(REMOVE)
