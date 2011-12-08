BINDIR = $(DESTDIR)/usr/bin
LAUNCHERDIR = $(DESTDIR)/usr/share/applications
ICONSDIR = $(DESTDIR)/usr/share/icons
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(BINDIR)
	cp src/kadro.py $(BINDIR)/kadro
	mkdir -p $(LAUNCHERDIR)
	cp kadro.desktop $(LAUNCHERDIR)/kadro.desktop
	mkdir -p $(ICONSDIR)
	cp kadro.svg $(ICONSDIR)/kadro.svg
uninstall:
	rm -f $(BINDIR)/kadro
	rm -f $(LAUNCHERDIR)/kadro.desktop
	rm -f $(ICONSDIR)/kadro.svg
	