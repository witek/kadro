BINDIR = $(DESTDIR)/usr/bin
LAUNCHERDIR = $(DESTDIR)/usr/share/applications
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(BINDIR)
	cp src/kadro.py $(BINDIR)/kadro
	mkdir -p $(LAUNCHERDIR)
	cp kadro.desktop $(LAUNCHERDIR)/kadro.desktop
uninstall:
	rm -f $(BINDIR)/kadro
	rm -f $(LAUNCHERDIR)/kadro.desktop
