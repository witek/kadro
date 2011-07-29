BINDIR = $(DESTDIR)/usr/bin
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(BINDIR)
	cp src/kadro.py $(BINDIR)/kadro
uninstall:
	rm -f $(BINDIR)/kadro

