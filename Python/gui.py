from gi import require_version
from os import path, makedirs
from platform import system
from subprocess import Popen
from configparser import ConfigParser
from time import sleep
import serial.tools.list_ports
import serial
from time import sleep, strftime
import webbrowser
require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
try:
    from os import startfile
    is_windows = True
except ImportError:
    is_windows = False

# configurations
cnfg = ConfigParser()
cnfg.read("settings.ini")
absolute_path = path.split(path.abspath(__file__))[0] + "/"
database_folder = absolute_path + cnfg.get("database","folder")
gallery_folder = absolute_path + cnfg.get("gallery","folder")
db_ext = "." + cnfg.get("database","extension")
date_format = cnfg.get("gallery","date_format")
auto_create_gallery = bool(cnfg.get("gallery","auto_create_gallery"))
baud_rate = int(cnfg.get("arduino","baud_rate"))
timeout = float(cnfg.get("arduino","timeout"))

def open_folder(folder):
    """
        Open a folder using the default file manager
    """
    if not path.exists(folder) and auto_create_gallery:
        makedirs(folder)
    if path.exists(folder):
        if system() == "Windows" and self.is_windows:
            startfile(folder)
        elif system() == "Darwin":
            Popen(["open", folder])
        else:
            Popen(["xdg-open", folder])

class GUI(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)
        self.set_title("Camera thermique GUI")
        self.set_default_size(300,150)
        self.resize(300,150)
        self.set_icon_from_file('logo.jpeg')
        self.set_border_width(10)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        vbox = Gtk.VBox(spacing=10)
        hbox1 = Gtk.HBox(spacing=10)
        hbox2 = Gtk.HBox(spacing=50)
        hbox3 = Gtk.HBox(spacing=50)
        # Actions Handler
        mb = Gtk.MenuBar()
        filemenu = Gtk.Menu()
        helpmenu = Gtk.Menu()
        filem = Gtk.MenuItem("File")
        filem.set_submenu(filemenu)
        helpm = Gtk.MenuItem("Help")
        helpm.set_submenu(helpmenu)

        open_gallery = Gtk.MenuItem("Open Gallery Folder")
        open_gallery.connect("activate", self.open_gallery)
        open_database = Gtk.MenuItem("Open Database Folder")
        open_database.connect("activate", self.open_database)
        exit = Gtk.MenuItem("Exit")
        exit.connect("activate", Gtk.main_quit)
        filemenu.append(open_gallery)
        filemenu.append(open_database)
        filemenu.append(exit)

        open_blog = Gtk.MenuItem("Our Blog")
        open_blog.connect("activate", self.open_blog)
        open_github = Gtk.MenuItem("Our Github repository")
        open_github.connect("activate", self.open_github)
        about_menu = Gtk.MenuItem("About")
        about_menu.connect("activate", self.show_about)
        helpmenu.append(open_blog)
        helpmenu.append(open_github)
        helpmenu.append(about_menu)
        mb.append(filem)
        mb.append(helpm)

        # Ports handler
        ports_label = Gtk.Label()
        ports_label.set_text("Port : ")
        ports_label.set_justify(Gtk.Justification.LEFT)
        self.ports = Gtk.ListStore(str)
        for port in serial.tools.list_ports.comports():
            self.ports.append([port[0]])
        self.ports_combo = Gtk.ComboBox.new_with_model(self.ports)
        self.ports_combo.connect("changed", self.on_port_changed)
        renderer_text = Gtk.CellRendererText()
        self.ports_combo.pack_start(renderer_text, True)
        self.ports_combo.add_attribute(renderer_text, "text", 0)
        self.ports_combo.set_active(0)
        hbox1.pack_start(ports_label, False, False, 0)
        hbox1.pack_start(self.ports_combo, False, False, 0)
        #Refresh button Handler
        self.eventbox = Gtk.EventBox()
        self.refresh_button = Gtk.Image()
        self.refresh_button.set_from_file("refresh.png")
        self.eventbox.add(self.refresh_button)
        self.eventbox.connect("button-press-event", self.refresh_ports)
        hbox1.pack_start(self.eventbox, True, True, 0)
        # Connect Button Handler
        self.connect_button = Gtk.Button.new_with_mnemonic("Connect")
        self.connect_button.connect("clicked", self.on_connect_clicked)
        hbox1.pack_start(self.connect_button, True, True, 0)
        #Message Label
        self.label = Gtk.Label()
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_no_show_all(True)
        #Progress bar
        self.start_button = Gtk.Button.new_with_mnemonic("Start")
        self.start_button.connect("clicked", self.start_capturing)
        self.start_button.set_no_show_all(True)
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        self.progressbar.set_fraction(0.0)
        self.progressbar.set_no_show_all(True)
        hbox2.pack_start(self.start_button, False, False, 0)
        hbox2.pack_start(self.progressbar, False, False, 0)
        #Save & show image
        self.save_image = Gtk.Button.new_with_mnemonic("Save Image")
        self.save_image.connect("clicked", self.save_image_clicked)
        self.save_image.set_no_show_all(True)
        self.show_image = Gtk.Button.new_with_mnemonic("Show Image")
        self.show_image.connect("clicked", self.show_image_clicked)
        self.show_image.set_no_show_all(True)
        hbox3.pack_start(self.show_image, False, False, 0)
        hbox3.pack_start(self.save_image, False, False, 0)

        vbox.pack_start(mb, False, False ,0)
        vbox.pack_start(hbox1, False, False, 0)
        vbox.pack_start(self.label, False, False, 0 )
        vbox.pack_start(hbox2, False, False, 0)
        vbox.pack_start(hbox3, False, False, 0)
        self.add(vbox)

    def on_port_changed(self, combo):
        """
            Update the port value
        """
        tree_iter = combo.get_active_iter()
        if tree_iter:
            model = combo.get_model()
            port = model[tree_iter][0]
            self.port = port

    def refresh_ports(self , eventbox, button):
        """
            Update ports lists (Combolist)
        """
        if self.ports_combo.get_sensitive():
            self.ports = Gtk.ListStore(str)
            for port in serial.tools.list_ports.comports():
                self.ports.append([port[0]])
            self.ports_combo.set_model(self.ports)
            self.ports_combo.set_active(0)


    def on_connect_clicked(self, button):
        """
            Connect button clicked event handler
        """
        global baud_rate , timeout
        self.label.set_text("Connecting..")
        self.refresh_button.set_sensitive(True)
        self.label.show()
        self.connect_button.set_sensitive(False)
        self.ports_combo.set_sensitive(False)
        if self.port:
            try :
                self.arduino = serial.Serial(self.port, baud_rate, timeout=timeout)
                if self.arduino.isOpen():
                    self.label.hide()
                    self.connect_button.set_label("Disconnect")
                    self.connect_button.connect("clicked", self.on_disconnect_clicked)
                    self.connect_button.set_sensitive(True)
                    self.start_button.show()
            except serial.serialutil.SerialException:
                self.label.set_text("Couldn't Connect, please try another Port")
                self.connect_button.set_sensitive(True)
                self.ports_combo.set_sensitive(True)

    def on_disconnect_clicked(self, button):
        """
            Disconnect button clicked event handler
        """
        if self.arduino.isOpen():
            self.arduino.close()
            self.label.set_no_show_all(True)
            self.label.hide()
            self.connect_button.set_sensitive(True)
            self.ports_combo.set_sensitive(True)
            self.progressbar.hide()
            self.start_button.hide()
            self.save_image.hide()
            self.show_image.hide()
            self.connect_button.set_label("Connect")
            self.connect_button.connect("clicked", self.on_connect_clicked)

    def start_capturing(self, button):
        """"
            Start capturing the thermal image
        """
        self.start_button.set_sensitive(False)
        self.connect_button.set_sensitive(False)
        self.progressbar.show()
        i = 0
        new_value = 0
        while i < 6400:
            self.progressbar.set_fraction(float(new_value))
            new_value += 0.015625
            i+=1
        self.progressbar.set_text("100%")
        self.start_button.set_sensitive(True)
        self.save_image.show()
        self.connect_button.set_sensitive(True)
        self.show_image.show()

    def open_gallery(self, widget):
        """"
            Open the gallery folder using the default file manager
        """
        global gallery_folder
        open_folder(gallery_folder)

    def open_database(self, widget):
        """
            Open the databaes folder using the default file manger
        """
        global database_folder
        open_folder(database_folder)

    def open_blog(self, widget):
        """
            Open the blog in the default web browser
        """
        webbrowser.open("https://tranh201groupe5.wordpress.com/")

    def open_github(self, widget):
        """"
            Open the github repository in the default web browser
        """
        webbrowser.open("https://github.com/archaicmuse/TRANH201-5")

    def show_image_clicked(self, button):
        """

        """
        pass

    def save_image_clicked(self, button):
        pass

    def show_about(self, widget):
        """
            Show the about dialog
        """
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self)
        dialog.set_program_name("Thermal Camera GUI")
        dialog.set_website("https://tranh201groupe5.wordpress.com")
        dialog.set_website_label("Website")
        logo = GdkPixbuf.Pixbuf.new_from_file("logo.jpeg")
        dialog.set_logo(logo)
        dialog.set_name('Thermal Camera GUI')
        dialog.set_authors(['Bilal ELMOUSSAOUI',
                            'Laurent STORRER',
                            'Aurélien MEUNIER',
                            'Alix GILLIARD',
                            'Eleonora DESY',
                            'Ayoub AZAIZAOUI',
                            'Andrew RYAN'])
        dialog.set_comments(' Created by students of Ecole Polytechnique DE BRUXELLES.')
        dialog.set_version("0.1 beta")
        dialog.run()
        dialog.destroy()


win = GUI()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()