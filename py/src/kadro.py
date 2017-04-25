# Copyright 2011 Witoslaw Koczewski (wi@koczewski.de)

import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk
from gi.repository import WebKit2
from gi.repository.GdkPixbuf import Pixbuf, InterpType

import json
import shutil
import stat
import webbrowser

class Config:

    work_dir = os.getenv("HOME") + "/.kadro"
    sites_dir = work_dir + "/sites"
    icons_dir = os.getenv("HOME") + "/.icons"

    def __init__(self):
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)
        print("Dir: " + self.work_dir)
        if not os.path.exists(self.sites_dir):
            os.mkdir(self.sites_dir)

    def get_site_dir(self, site):
        return self.sites_dir + "/" + site

    def get_launcher_file_path(self, site):
        return os.getenv("HOME") + "/.local/share/applications/kadro-" + site + ".desktop"

    def get_starter_file_path(self, site):
        return self.get_site_dir(site) + "/" + site + ".py"

    def get_site_icon_name(self, site):
        return "kadro-" + site

    def get_site_icon_path(self, site):
        icon_name = self.get_site_icon_name(site)
        file = self.icons_dir + "/" + icon_name + ".svg"
        if os.path.exists(file):
            return file
        file = self.icons_dir + "/" + icon_name + ".png"
        if os.path.exists(file):
            return file
        file = self.icons_dir + "/" + icon_name + ".gif"
        if os.path.exists(file):
            return file
        file = self.icons_dir + "/" + icon_name + ".jpg"
        if os.path.exists(file):
            return file
        file = self.icons_dir + "/" + icon_name + ".tif"
        if os.path.exists(file):
            return file
        file = self.icons_dir + "/" + icon_name + ".xpm"
        if os.path.exists(file):
            return file
        return None

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

        oldstarter = self.get_site_dir(site) + "/start.sh"
        if os.path.exists(oldstarter):
            print("Upgrading site config: " + config_file_path)
            self.save_site_config(data, None)
            os.remove(oldstarter)

        oldstarter = self.get_site_dir(site) + "/start.py"
        if os.path.exists(oldstarter):
            print("Upgrading site config: " + config_file_path)
            self.save_site_config(data, None)
            os.remove(oldstarter)

        return data

    def load_site_configs(self):
        configs = []
        for file in os.listdir(self.sites_dir):
            config = self.load_site_config(file)
            configs.append(config)
        return configs

    def save_site_config(self, site_config, new_icon_path):
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
            file.write("#! /usr/bin/python\n")
            file.write("import kadro\n")
            file.write("kadro.startbrowser('" + site + "')\n")
        os.chmod(starter_file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IROTH)

        if new_icon_path:
            tmp_file = site_dir + "/icon.tmp"
            shutil.copyfile(new_icon_path, tmp_file)
            icon_name = "kadro-" + site
            file = self.icons_dir + "/" + icon_name + ".svg"
            if os.path.exists(file):
                os.remove(file)
            file = self.icons_dir + "/" + icon_name + ".png"
            if os.path.exists(file):
                os.remove(file)
            file = self.icons_dir + "/" + icon_name + ".gif"
            if os.path.exists(file):
                os.remove(file)
            file = self.icons_dir + "/" + icon_name + ".jpg"
            if os.path.exists(file):
                os.remove(file)
            file = self.icons_dir + "/" + icon_name + ".tif"
            if os.path.exists(file):
                os.remove(file)
            file = self.icons_dir + "/" + icon_name + ".xpm"
            if os.path.exists(file):
                os.remove(file)
            suffix = os.path.splitext(new_icon_path)[1];
            os.rename(tmp_file, self.icons_dir + "/" + icon_name + suffix)

        launcher_file_path = self.get_launcher_file_path(site)
        with open(launcher_file_path, mode='w') as file:
            file.write("[Desktop Entry]\n")
            file.write("Name=" + site_config["title"] + "\n")
            file.write("Comment=Open site with Kadro: " + site + " -> " + site_config["url"] + "\n")
            file.write("Icon=kadro-" + site + "\n")
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

    def start_site(self, site, config_mode=False):
        starter_file_path = self.get_starter_file_path(site)
        print "Starting site: " + starter_file_path
        #ret = os.spawnv(os.P_NOWAIT, starter_file_path,[])
        #pipe = os.popen('{ ' + starter_file_path + '; } 2>&1', 'r')
        config_option = ""
        if config_mode:
            config_option = " --config"
        os.system(starter_file_path + config_option + " &")


class Browser:

    # http://www.eurion.net/python-snippets/snippet/Webkit%20Browser.html
    # http://webkitgtk.org/reference/webkitgtk/stable/
    # http://webkitgtk.org/reference/webkit2gtk/stable/WebKitCookieManager.html#webkit-cookie-manager-set-persistent-storage

    site = None
    site_config = {}
    title = None
    url = None
    width = None
    height = None

    def __init__(self, site):
        self.site = site

    def start(self):

        def on_destroy(mozembed):
            Gtk.main_quit()

        def on_resize(mozembed):
            size = self.win.get_size()
            width = size[0]
            height = size[1]
            if self.site_config.has_key("width") and self.site_config["width"] == width and self.site_config.has_key("height") and self.site_config["height"] == height:
                return
            self.site_config["width"] = width
            self.site_config["height"] = height
            config.save_site_config(self.site_config, None)

        def on_open_uri(mozembed, uri):
            print "Requested URI: " + uri
            return False

        def on_new_window(mozembed, retval, chromemask):
            print "on_new_window(" + str(mozembed) + ", " + str(retval) + ", " + str(chromemask) + ")"
            url = mozembed.get_link_message()
            if not url:
                print "ERROR: new-window without URL"
                return None
            print "Calling default web browser: " + url
            webbrowser.open(url)
            return None

        def on_activate_link():
            print "on_activate_link"

        site_dir = config.get_site_dir(self.site)

        print "Starting site: " + site_dir
        self.updateSelf()

        self.web_view = WebKit2.WebView()
        # self.web_view.connect("activate-link", on_activate_link)

        web_context = self.web_view.get_context();
        data_manager =  web_context.get_website_data_manager()
        cookie_manager = web_context.get_cookie_manager()
        cookie_manager.set_persistent_storage(site_dir+"/cookies.txt", WebKit2.CookiePersistentStorage.TEXT)
        self.web_view.load_uri(self.url)

        self.win = Gtk.Window()
        self.win.set_title(self.title)
        self.win.set_default_size(self.width, self.height)
        icon_path = config.get_site_icon_path(self.site)
        if icon_path:
            self.win.set_icon_from_file(icon_path)
        self.win.set_icon_name(config.get_site_icon_name(self.site))
        self.win.add(self.web_view)
        # self.win.add(Gtk.LinkButton("http://www.gtk.org", "Visit GTK+ Homepage"))
        self.win.connect("destroy", on_destroy)
        self.win.connect('check-resize', on_resize)
        self.win.show_all()

        Gtk.main()


    def updateSelf(self):
        if not self.site:
            raise "self.site not set"

        self.site_config = config.load_site_config(self.site)

        if not self.url and self.site_config.has_key("url"):
            self.url = self.site_config["url"]
        if not self.url:
            raise "URL not defined for site " + self.site

        if not self.title and self.site_config.has_key("title"):
            self.title = self.site_config["title"]
        if not self.title:
            self.title = self.site

        if not self.width and self.site_config.has_key("width"):
            self.width = self.site_config["width"]
        if not self.width:
            self.width = 800

        if not self.height and self.site_config.has_key("height"):
            self.height = self.site_config["height"]
        if not self.height:
            self.height = 600


class SiteConfigurator:

    site_config = {}
    save_callback = None

    entries = []
    entries_table = None
    last_entry_row = 0
    name_entry = None
    icon_path = None

    def __init__(self, site_config, save_callback):
        self.site_config = site_config
        self.save_callback = save_callback

    def start(self):
        def on_cancel(button):
            self.win.hide()

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
            config.save_site_config(self.site_config, self.icon_path)

            self.win.hide()
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

        self.entries_table = Gtk.Table(columns=2, homogeneous=False)
        self.entries_table.set_col_spacing(0, 10)
        self.append_entry("Title", "title", extension_func=title_extension_func)
        self.append_entry("URL", "url")
        self.append_entry("Name", "name", readonly=name_readonly, extension_func=name_extension)
        self.append_icon_editor()

        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect("clicked", on_cancel)

        save_button = Gtk.Button("Save")
        save_button.connect("clicked", on_save)

        buttons_box = Gtk.HBox()
        buttons_box.pack_end(save_button, False, False, 0)
        buttons_box.pack_end(cancel_button, False, False, 10)

        main_box = Gtk.VBox()
        main_box.pack_start(self.entries_table, True, True, 0)
        main_box.pack_start(buttons_box, False, False, 10)

        self.win = Gtk.Window()
        self.win.set_title(title_prefix + " - Kadro")
        self.win.set_position(Gtk.WindowPosition.CENTER)
        self.win.set_border_width(10)
        self.win.add(main_box)
        self.win.show_all()

    def append_icon_editor(self):
        label = Gtk.Label("Icon")

        site = None
        if self.site_config.has_key("name"):
            site = self.site_config["name"]

        image = Gtk.Image()
        image.set_size_request(48, 48)

        if site:
            self.icon_path = config.get_site_icon_path(site)

        def update_image():
            if self.icon_path:
                image.set_from_pixbuf(Pixbuf.new_from_file(self.icon_path).scale_simple(48, 48, InterpType.BILINEAR))

        update_image()

        def on_select_icon(button):
            dialog = Gtk.FileChooserDialog("Open..", self.win, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            dialog.set_default_response(Gtk.ResponseType.OK)

            filter = Gtk.FileFilter()
            filter.set_name("Images")
            filter.add_mime_type("image/png")
            filter.add_mime_type("image/jpeg")
            filter.add_mime_type("image/gif")
            filter.add_mime_type("image/svg")
            filter.add_mime_type("image/svg+xml")
            filter.add_pattern("*.png")
            filter.add_pattern("*.jpg")
            filter.add_pattern("*.gif")
            filter.add_pattern("*.tif")
            filter.add_pattern("*.xpm")
            filter.add_pattern("*.svg")
            dialog.add_filter(filter)

            if self.icon_path:
                dialog.set_filename(self.icon_path)

            usr_share_icons_path = "/usr/share/icons"
            if os.path.exists(usr_share_icons_path):
                dialog.add_shortcut_folder(usr_share_icons_path)

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.icon_path = dialog.get_filename()
                update_image()
            dialog.destroy()

        button = Gtk.Button()
        button.set_image(image)
        button.connect("clicked", on_select_icon)

        box = Gtk.HBox()
        box.pack_start(button, False, False, 0)

        row = self.last_entry_row + 1
        self.entries_table.attach(label, 0, 1, row, row + 1)
        self.entries_table.attach(box, 1, 2, row, row + 1)
        self.last_entry_row = row

    def append_entry(self, label_text, property_name, readonly=False, extension_func=None):
        label = Gtk.Label(label_text)

        entry = Gtk.Entry()
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
    config_button = None
    delete_button = None

    def start(self):
        print "Starting configurator"

        def name_func(column, cell, model, iter, xxx):
            title = "untitled"
            site_config = model.get_value(iter, 0)
            if site_config.has_key("title"):
                title = site_config["title"]
            cell.set_property('text', title)

        def on_destroy(mozembed):
            Gtk.main_quit()

        def on_start_site(button):
            site_config = self.get_selected_site_config()
            config.start_site(site_config["name"])

        def on_config_site(button):
            site_config = self.get_selected_site_config()
            config.start_site(site_config["name"], config_mode=True)

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

        sites_list_name_cell = Gtk.CellRendererText()
        sites_list_name_col = Gtk.TreeViewColumn("Sites", sites_list_name_cell)
        sites_list_name_col.set_cell_data_func(sites_list_name_cell, name_func)
        self.sites_list = Gtk.TreeView()
        self.sites_list.append_column(sites_list_name_col)
        self.sites_list.connect("cursor-changed", on_select)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_size_request(200, 300)
        scrolledwindow.add(self.sites_list)

        self.start_button = Gtk.Button("Start")
        self.start_button.connect("clicked", on_start_site)

        self.edit_button = Gtk.Button("Properties")
        self.edit_button.connect("clicked", on_edit_site)

        #self.config_button = Gtk.Button("Mozilla Config")
        #self.config_button.connect("clicked", on_config_site)

        self.delete_button = Gtk.Button("Delete")
        self.delete_button.connect("clicked", on_delete_site)

        add_button = Gtk.Button("New Site")
        add_button.connect("clicked", on_add_site)

        buttons_box = Gtk.VBox()
        buttons_box.set_spacing(5)
        buttons_box.pack_start(self.start_button, False, False, 10)
        buttons_box.pack_start(self.edit_button, False, False, 0)
        #buttons_box.pack_start(self.config_button, False, False, 0)
        buttons_box.pack_start(self.delete_button, False, False, 0)
        buttons_box.pack_start(add_button, False, False, 10)

        main_box = Gtk.HBox()
        main_box.pack_start(scrolledwindow, True, True, 0)
        main_box.pack_start(buttons_box, False, True, 10)

        self.win = Gtk.Window()
        self.win.set_title("Kadro")
        #self.win.set_position(Gtk.WIN_POS_CENTER)
        self.win.set_border_width(10)
        self.win.add(main_box)
        self.win.connect("destroy", on_destroy)
        self.win.show_all()

        self.update_sites_list()
        Gtk.main()

    def update_buttons_sensitivity(self):
        sensitive = self.get_selected_site_config() != None
        self.start_button.set_sensitive(sensitive)
        self.edit_button.set_sensitive(sensitive)
        #self.config_button.set_sensitive(sensitive)
        self.delete_button.set_sensitive(sensitive)

    def update_sites_list(self):
        self.sites_list_model = Gtk.ListStore(object)
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
    parser.add_argument('-c', '--config', action='store_true', help='Start with Mozilla configuration page')
    args = parser.parse_args()
    return args


def startbrowser(site):
    site_dir = config.get_site_dir(site)
    if not os.path.exists(site_dir):
        showerror(None, "Site dir does not exist: " + site_dir)
        startconfigurator(config)
        return
    browser = Browser(site)
    if mozconfig:
        browser.url = "about:config"
    browser.start()


def startconfigurator():
    Configurator().start()


def showerror(parent, message):
    print "ERROR: " + message
    md = gtk.MessageDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message)
    md.run()
    md.destroy()


print "Initializing Kadro"
config = Config()

args = parseargs()

mozconfig = args.config
