#!/usr/bin/python

import gtk
import gtk.glade
import time

import common


class LocalXchangeGUI:
    def __init__(self):
        self.specFileName = "localxchange.glade"
        
        self.systems = common.start_system()
    
    def Show_main(self):
        self.wmtree = gtk.glade.XML(self.specFileName, "window_main")
        self.wmtree.signal_autoconnect(self)
        
    def Show_findoptions(self, on_host):
        self.wftree = gtk.glade.XML(self.specFileName, "window_find")
        self.wftree.signal_autoconnect(self)
        print "search on "+on_host
        
    def GUI_hide_function(self, obj):
        print "hiding"
        obj.hide()
        
    def GUI_open_function(self, obj):
        self.motree = gtk.glade.XML(self.specFileName, "menu_open")
        self.motree.signal_autoconnect(self)
        menu = self.motree.get_widget("menu_open")
        menu.popup(None, None, None, 1, 0)
        return True
    
    def generate_searchmenu(self):
        menu = gtk.Menu()
        all_hosts = gtk.MenuItem("Su tutti gli host")
        all_hosts.connect("activate", self.Show_findoptions, "all")
        all_hosts.show()
        menu.append(all_hosts)
        for host in self.systems['nodemanager']:
            menuitem = gtk.MenuItem(host)
            menuitem.connect("activate", self.Show_findoptions, host)
            menuitem.show()
            menu.append(menuitem)
        return menu
        
    def GUI_search_function(self, obj):
        #self.mstree = gtk.glade.XML(self.specFileName, "menu_find")
        #self.mstree.signal_autoconnect(self)
        #menu = self.mstree.get_widget("menu_find")
        menu = self.generate_searchmenu()
        menu.popup(None, None, None, 1, 0)
        return True
        
    def GUI_news_function(self, obj):
        pass
    
    def GUI_disk_function(self, obj):
        pass
    
    def GUI_about_function(self, obj):
        self.watree = gtk.glade.XML(self.specFileName, "aboutdialog1")
        self.watree.signal_autoconnect(self)
    
    def GUI_search_submit_function(self, obj):
        pass
    
    def GUI_exit_function(self, *objs):
        gtk.main_quit()
    
    def MainLoop(self):
        gtk.main()


gui = LocalXchangeGUI()
gui.Show_main()
gui.MainLoop()
