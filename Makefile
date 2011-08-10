BINDIR = $(DESTDIR)/$(bindir)
DATADIR = $(DESTDIR)/$(datadir)
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(BINDIR)
	cp src/kadro.py $(BINDIR)/kadro
	cp kadro.desktop $(DATADIR)/applications/kadro.desktop
uninstall:
	rm -f $(BINDIR)/kadro
	rm -f $(DATADIR)/applications/kadro.desktop

