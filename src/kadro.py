#! /usr/bin/python

# Copyright 2011 Witoslaw Koczewski (wi@koczewski.de)

import os
import gtk
import gtkmozembed
import json
import shutil
import stat

class Config:
    
    work_dir = os.getenv("HOME") + "/.kadro"
    sites_dir = work_dir + "/sites"

    def __init__(self):
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)
        if not os.path.exists(self.sites_dir):
            os.mkdir(self.sites_dir)

    def get_site_dir(self, site):
        return self.sites_dir + "/" + site

    def get_launcher_file_path(self, site):
        return os.getenv("HOME") + "/.local/share/applications/kadro-" + site + ".desktop"

    def get_starter_file_path(self, site):
        return self.get_site_dir(site) + "/start.sh"

    def has_site(self, site):
        site_dir = self.get_site_dir(site)
        return os.path.exists(site_dir)

    def load_site_config(self, site):
        config_file_path = self.get_site_dir(site) + "/config.json"
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
    
    def save_site_config(self, site_config):
        site = site_config["name"]
        site_dir = self.get_site_dir(site)
        if not os.path.exists(site_dir):
            os.mkdir(site_dir)
        
        config_file_path = site_dir + "/config.json"
        print "Saving site: " + config_file_path
        with open(config_file_path, mode='w') as file:
            json.dump(site_config, file)
        
        starter_file_path = self.get_starter_file_path(site)
        with open(starter_file_path, mode='w') as file:
            file.write("#!/bin/sh\n" + os.path.realpath(__file__) + " " + site)
        os.chmod(starter_file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IROTH)
        
        launcher_file_path = self.get_launcher_file_path(site)
        with open(launcher_file_path, mode='w') as file:
            file.write("[Desktop Entry]\n")
            file.write("Name=" + site_config["title"] + "\n")
            file.write("Comment=Open site with Kadro: " + site + " -> " + site_config["url"] + "\n")
            file.write("Icon=\n")
            file.write("Exec=" + starter_file_path + "\n")
            file.write("Categories=Network;\n")
            file.write("Type=Application\n")
    
    def delete_site(self, site):
        site_dir = self.get_site_dir(site)
        print "Deleting site: " + site_dir

        launcher_file_path = self.get_launcher_file_path(site)
        if os.path.exists(launcher_file_path):
            os.remove(launcher_file_path)
        
        if not os.path.exists(site_dir):
            return
        tmp_dir = self.work_dir + "/tmp"
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        shutil.move(site_dir, tmp_dir)
        shutil.rmtree(tmp_dir, True)

    def start_site(self, site):
        starter_file_path = self.get_starter_file_path(site)
        print "Starting site: " + starter_file_path
        #ret = os.spawnv(os.P_NOWAIT, starter_file_path,[])
        #pipe = os.popen('{ ' + starter_file_path + '; } 2>&1', 'r')
        os.system(starter_file_path + " &")

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

        site_dir = config.get_site_dir(self.site)

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
    save_callback = None
    
    entries = []
    entries_table = None
    last_entry_row = 0
    name_entry = None
    
    def __init__(self, site_config, save_callback):
        self.site_config = site_config
        self.save_callback = save_callback
        
    def start(self):
        def on_cancel(button):
            self.win.hide_all()
            
        def on_save(button):
            for entry in self.entries:
                value = entry.get_text()
                property_name = entry.site_config_property_name
                if not value or value.strip() == "":
                    label = entry.site_config_label_text
                    showerror(self.win, '"' + label + '" is mandatory')
                    return
                self.site_config[property_name] = value.strip()
            site = self.site_config["name"]
            if (not self.site_config.has_key("persistant")) and config.has_site(site):
                    showerror(self.win, 'Site with the name "' + site + '" already exists.')
                    return                
            config.save_site_config(self.site_config)
            self.win.hide_all()
            self.save_callback()
        
        def on_title_entry_focus_out(title_entry, event):
            text = self.name_entry.get_text()
            if text and text.strip() != "":
                return
            text = title_entry.get_text()
            if not text or text.strip() == "":
                return
            text = text.strip()
            text = text.lower()
            text = text.replace('http://', '')
            text = text.replace('https://', '')
            text = text.replace(' ', '')
            text = text.replace('/', '')
            text = text.replace('\\', '')
            text = text.replace(':', '')
            self.name_entry.set_text(text)
        
        def title_extension(title_entry):
            title_entry.connect("focus-out-event", on_title_entry_focus_out)
            
        def name_extension(name_entry):
            self.name_entry = name_entry
        
        title_prefix = "New site"
        if self.site_config.has_key("title"):
            title_prefix = self.site_config["title"]

        name_readonly = self.site_config.has_key("name")
        title_extension_func = None
        if not name_readonly:
            title_extension_func = title_extension
        
        self.entries_table = gtk.Table(columns=2, homogeneous=False)
        self.entries_table.set_col_spacing(0, 10)
        self.append_entry("Title", "title", extension_func=title_extension_func)
        self.append_entry("URL", "url")
        self.append_entry("Name", "name", readonly=name_readonly, extension_func=name_extension)
        
        cancel_button = gtk.Button("Cancel")
        cancel_button.connect("clicked", on_cancel)
        
        save_button = gtk.Button("Save")
        save_button.connect("clicked", on_save)
        
        buttons_box = gtk.HBox()
        buttons_box.pack_end(save_button, False, False)
        buttons_box.pack_end(cancel_button, False, False, 10)
        
        main_box = gtk.VBox()
        main_box.pack_start(self.entries_table, True, True)
        main_box.pack_start(buttons_box, False, False, 10)
        
        self.win = gtk.Window()
        self.win.set_title(title_prefix + " - Kadro")
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_border_width(10)
        self.win.add(main_box)
        self.win.show_all()

    def append_entry(self, label_text, property_name, readonly=False, extension_func=None):
        label = gtk.Label(label_text)
        
        entry = gtk.Entry()
        entry.set_width_chars(80)
        entry.set_sensitive(not readonly)
        entry.site_config_property_name = property_name
        entry.site_config_label_text = label_text
        if self.site_config.has_key(property_name):
            entry.set_text(self.site_config[property_name])
        if extension_func:
            extension_func(entry)
        self.entries.append(entry)
        
        row = self.last_entry_row + 1
        self.entries_table.attach(label, 0, 1, row, row + 1)
        self.entries_table.attach(entry, 1, 2, row, row + 1)
        self.last_entry_row = row

class Configurator:
    
    sites_list = None
    sites_list_model = None
    edit_button = None
    delete_button = None
    
    def start(self):
        print "Starting configurator"

        def onDestroy(mozembed):
            gtk.main_quit()

        def name_func(column, cell, model, iter):
            title = "untitled"
            site_config = model.get_value(iter, 0)
            if site_config.has_key("title"):
                title = site_config["title"]
            cell.set_property('text', title)

        def on_start_site(button):
            site_config = self.get_selected_site_config()
            config.start_site(site_config["name"])

        def on_edit_site(button):
            site_config = self.get_selected_site_config()
            SiteConfigurator(site_config, self.update_sites_list).start()
            
        def on_delete_site(button):
            site_config = self.get_selected_site_config()
            config.delete_site(site_config["name"])
            self.update_sites_list()

        def on_add_site(button):
            SiteConfigurator({}, self.update_sites_list).start()

        def on_select(list):
            self.update_buttons_sensitivity()

        sites_list_name_cell = gtk.CellRendererText()
        sites_list_name_col = gtk.TreeViewColumn("Sites", sites_list_name_cell)
        sites_list_name_col.set_cell_data_func(sites_list_name_cell, name_func)
        self.sites_list = gtk.TreeView()
        self.sites_list.append_column(sites_list_name_col)
        self.sites_list.connect("cursor-changed", on_select)
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_size_request(200, 300)
        scrolledwindow.add(self.sites_list)
        
        self.start_button = gtk.Button("Start")
        self.start_button.connect("clicked", on_start_site)
        
        self.edit_button = gtk.Button("Edit site...")
        self.edit_button.connect("clicked", on_edit_site)
        
        self.delete_button = gtk.Button("Delete site")
        self.delete_button.connect("clicked", on_delete_site)
        
        add_button = gtk.Button("Add site...")
        add_button.connect("clicked", on_add_site)

        buttons_box = gtk.VBox()
        buttons_box.set_spacing(5)
        buttons_box.pack_start(self.start_button, False, False, 10)
        buttons_box.pack_start(self.edit_button, False, False)
        buttons_box.pack_start(self.delete_button, False, False)
        buttons_box.pack_start(add_button, False, False, 10)

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
    
    def update_buttons_sensitivity(self):
        sensitive = self.get_selected_site_config() != None
        self.start_button.set_sensitive(sensitive)
        self.edit_button.set_sensitive(sensitive)
        self.delete_button.set_sensitive(sensitive)
        
    def update_sites_list(self):
        self.sites_list_model = gtk.ListStore(object)
        site_configs = config.load_site_configs()
        for site_config in site_configs:
            self.sites_list_model.append([site_config])
        self.sites_list.set_model(self.sites_list_model)
        self.update_buttons_sensitivity()

    def get_selected_site_config(self):
        iter = self.sites_list.get_selection().get_selected()[1]
        if not iter:
            return None
        site_config = self.sites_list_model.get_value(iter, 0)
        return site_config
        

def parseargs():
    import argparse
    parser = argparse.ArgumentParser(description='Kadro dedicated browser.')
    parser.add_argument('site', nargs='?', help='site of the site to start')
    args = parser.parse_args()
    return args


def startbrowser(site, config):
    site_dir = config.get_site_dir(site)
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
