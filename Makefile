
install:
	/bin/cp -fr ../sweetpotato /opt/ && ln -s /opt/sweetpotato/sweetpotato.py /usr/bin/sweetpotato

uninstall:
	/bin/rm -fr /opt/sweetpotato /usr/bin/sweetpotato

