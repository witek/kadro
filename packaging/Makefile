LIBDIR = $(DESTDIR)/usr/lib/kadro
BINDIR = $(DESTDIR)/usr/bin
LAUNCHERDIR = $(DESTDIR)/usr/share/applications
ICONSDIR = $(DESTDIR)/usr/share/icons

build:

clean:
	rm -rf kadro-linux-x64

install:
	mkdir -p $(LIBDIR)
	cp -r kadro-linux-x64/* $(LIBDIR)
	mkdir -p $(BINDIR)
	ln -sf /usr/lib/kadro/kadro $(BINDIR)/kadro
	mkdir -p $(LAUNCHERDIR)
	cp kadro.desktop $(LAUNCHERDIR)/kadro.desktop
	mkdir -p $(ICONSDIR)
	cp kadro.svg $(ICONSDIR)/kadro.svg

uninstall:
	rm -rf $(LIBDIR)
	rm -f $(BINDIR)/kadro
	rm -f $(LAUNCHERDIR)/kadro.desktop
	rm -f $(ICONSDIR)/kadro.svg
