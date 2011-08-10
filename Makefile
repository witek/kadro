BINDIR = $(DESTDIR)/$(bindir)
DATADIR = $(DESTDIR)/$(datadir)
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(BINDIR)
	cp src/kadro.py $(BINDIR)/kadro
	/usr/share/applications
uninstall:
	rm -f $(BINDIR)/kadro

