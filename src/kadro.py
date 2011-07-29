#! /usr/bin/python

# Copyright 2011 Witoslaw Koczewski (wi@koczewski.de)

import os
import gtk
import gtkmozembed

class Config:
    
    work_dir = os.getenv("HOME") + "/.kadro"
    sites_dir = work_dir + "/sites"
    
    def site_dir(self, site):
        return self.sites_dir + "/" + site
            

class Browser:
    
    site = None
    title = None
    url = None
    width = None
    height = None
    
    def __init__(self, site):
        self.site = site
    
    
    def start(self):
        
        
        def onDestroy(mozembed):
            gtk.main_quit()

        def onOpenUri(mozembed, uri):
            print "Requested URI: " +uri
            return False

        site_dir = config.sites_dir(self.site)

        print "Starting site: " + site_dir
        self.updateSelf()
        
        gtkmozembed.set_profile_path(site_dir, "profile")
        
        self.mozembed = gtkmozembed.MozEmbed()
        self.mozembed.load_url(self.url)
        self.mozembed.set_size_request(self.width, self.height)
        self.mozembed.connect("open-uri", onOpenUri)
        self.mozembed.show()

        self.win = gtk.Window()
        self.win.set_title(self.title)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.add(self.mozembed)
        self.win.connect("destroy", onDestroy)
        self.win.show()
        
        gtk.main()
        
        
    def updateSelf(self):
        if not self.site:
            raise "self.site not set"
        if not self.url:
            self.url = self.site
        if not self.title:
            self.title = self.site
        if not self.width:
            self.width = 1200
        if not self.height:
            self.height = 800
            

class Configurator:
    
    def start(self):
        print "Starting configurator"


def parseargs():
    import argparse
    parser = argparse.ArgumentParser(description='Kadro dedicated browser.')
    parser.add_argument('site', nargs='?', help='name of the site to start')
    args = parser.parse_args()
    return args


def startbrowser(site, config):
    site_dir = config.site_dir(site)
    if not os.path.exists(site_dir):
        showerror(None, "Site dir does not exist: " + site_dir)
        startconfigurator(config)
        return
    Browser(site).start()


def startconfigurator(config):
    Configurator().start()


def showerror(parent, message):
    print "ERROR: " + message
    md = gtk.MessageDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message)
    md.run()
    md.destroy()    


args = parseargs()

print "Initializing Kadro"
config = Config()

site = args.site

if site:
    startbrowser(site, config)
else:
    startconfigurator(config)
