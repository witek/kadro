LIBDIR = $(DESTDIR)/usr/lib/python2.7
BINDIR = $(DESTDIR)/usr/bin
LAUNCHERDIR = $(DESTDIR)/usr/share/applications
ICONSDIR = $(DESTDIR)/usr/share/icons
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(LIBDIR)
	cp src/kadro.py $(LIBDIR)/kadro.py
	mkdir -p $(BINDIR)
	cp src/kadro-configurator.py $(BINDIR)/kadro-configurator
	mkdir -p $(LAUNCHERDIR)
	cp kadro.desktop $(LAUNCHERDIR)/kadro.desktop
	mkdir -p $(ICONSDIR)
	cp kadro.svg $(ICONSDIR)/kadro.svg
uninstall:
	rm -f $(LIBDIR)/kadro.py[co]
	rm -f $(BINDIR)/kadro-configurator
	rm -f $(LAUNCHERDIR)/kadro.desktop
	rm -f $(ICONSDIR)/kadro.svg
	