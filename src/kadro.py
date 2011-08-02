#! /usr/bin/python

# Copyright 2011 Witoslaw Koczewski (wi@koczewski.de)

import os
import gtk
import gtkmozembed
import json

class Config:
    
    work_dir = os.getenv("HOME") + "/.kadro"
    sites_dir = work_dir + "/sites"
    
    def site_dir(self, site):
        return self.sites_dir + "/" + site

    def load_site_config(self, site):
        config_file_path = self.site_dir(site) + "/config.json"
        print("Loading site config: " + config_file_path)
        if not os.path.exists(config_file_path):
            return {}
        config_file = open(config_file_path)
        data = json.load(config_file)
        config_file.close()
        
        data["name"] = site
        data["persistant"] = True
        
        return data
    
    def load_site_configs(self):
        configs = []
        for file in os.listdir(self.sites_dir):
            config = self.load_site_config(file)
            configs.append(config)
        return configs
        

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
            print "Requested URI: " + uri
            return False

        site_dir = config.site_dir(self.site)

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

        site_config = config.load_site_config(self.site)
        
        if not self.url:
            self.url = site_config["url"]
            if not self.url:
                raise "URL not defined for site " + self.site
            
        if not self.title:
            self.title = site_config["title"]
            if not self.title:
                self.title = self.site
        
        if not self.width:
            self.width = 1200
        if not self.height:
            self.height = 800


class SiteConfigurator:
    
    site_config = {}
    
    def __init__(self, site_config):
        self.site_config = site_config
        
    def start(self):       
        title_prefix = "New site"
        if self.site_config.has_key("title"):
            title_prefix = self.site_config["title"]
        
        self.win = gtk.Window()
        self.win.set_title(title_prefix + " - Kadro")
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_border_width(10)
        #self.win.add(scrolledwindow)
        self.win.show_all()
        

class Configurator:
    
    sites_list = None
    
    def start(self):
        print "Starting configurator"

        def onDestroy(mozembed):
            gtk.main_quit()

        def name_func(column, cell, model, iter):
            cell.set_property('text', model.get_value(iter, 0))

        def on_add_site(widget):
            SiteConfigurator({}).start()

        sites_list_name_cell = gtk.CellRendererText()
        sites_list_name_col = gtk.TreeViewColumn('Site', sites_list_name_cell)
        sites_list_name_col.set_cell_data_func(sites_list_name_cell, name_func)
        self.sites_list = gtk.TreeView()
        self.sites_list.append_column(sites_list_name_col)
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.add(self.sites_list)
        
        add_button = gtk.Button("Add site...")
        add_button.connect("clicked", on_add_site)

        buttons_box = gtk.VBox()
        buttons_box.pack_start(add_button, False, True)

        main_box = gtk.HBox()
        main_box.pack_start(scrolledwindow, True, True)
        main_box.pack_start(buttons_box, False, True, 10)

        self.win = gtk.Window()
        self.win.set_title("Kadro")
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_border_width(10)
        self.win.add(main_box)
        self.win.connect("destroy", onDestroy)
        self.win.show_all()
        
        self.update_sites_list()
        gtk.main()
    
        
    def update_sites_list(self):
        model = gtk.ListStore(object)
        site_configs = config.load_site_configs()
        for site_config in site_configs:
            model.append([site_config["title"]])
        self.sites_list.set_model(model)


def parseargs():
    import argparse
    parser = argparse.ArgumentParser(description='Kadro dedicated browser.')
    parser.add_argument('site', nargs='?', help='site of the site to start')
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
