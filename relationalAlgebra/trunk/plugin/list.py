 
#!/usr/bin/python

# ZetCode PyGTK tutorial 
#
# This example shows a TreeView widget
# in a list view mode
#
# author: jan bodnar
# website: zetcode.com 
# last edited: February 2009


import gtk



class PyApp(gtk.Window):
    def __init__(self,data):
        super(PyApp, self).__init__()
        
        self.__data=data
        self.__header=self.__data[0]
        self.set_size_request(350, 250)
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.connect("destroy", gtk.main_quit)
        self.set_title("Result")

        vbox = gtk.VBox(False, 8)
        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        vbox.pack_start(sw, True, True, 0)

        store = self.create_model()

        treeView = gtk.TreeView(store)
        treeView.set_rules_hint(True)
        sw.add(treeView)

        self.create_columns(treeView)
        self.statusbar = gtk.Statusbar()
        
        vbox.pack_start(self.statusbar, False, False, 0)

        self.add(vbox)
        self.show_all()


    def create_model(self):
        
        
        store = gtk.ListStore(*([str] * len(self.__header)))

        for i in range(1,len(self.__data)):
            store.append(self.__data[i])

        return store


    def create_columns(self, treeView):
        for i in range(0,len(self.__header)):
            rendererText = gtk.CellRendererText()
            new=self.__header[i].replace('_','_ ')
            column = gtk.TreeViewColumn(new, rendererText, text=i)
            column.set_sort_column_id(i)
            treeView.append_column(column)
