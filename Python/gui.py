#!/usr/bin/python
from gi import require_version
from os import path, makedirs
from platform import system
from subprocess import Popen
from configparser import ConfigParser
from serial.tools.list_ports import comports
import serial
from time import sleep, strftime, gmtime
import webbrowser
from pylab import get_cmap
import matplotlib.pyplot as plt
import numpy as np
import csv
import threading
import queue

require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk
try:
    from os import startfile
    is_windows = True
except ImportError:
    is_windows = False

# configurations
Gdk.threads_init()
cnfg = ConfigParser()
cnfg.read("settings.ini")
absolute_path = path.split(path.abspath(__file__))[0] + "/"
database_folder = absolute_path + cnfg.get("database","folder")
gallery_folder = absolute_path + cnfg.get("gallery","folder")
db_ext = "." + cnfg.get("database","extension")
date_format = "%d-%m-%Y_%H-%M-%S"
auto_create_gallery = bool(cnfg.get("gallery","auto_create_gallery"))
baud_rate = int(cnfg.get("arduino","baud_rate"))
timeout = float(cnfg.get("arduino","timeout"))
xpixel = int(cnfg.get("arduino","xpixel"))
ypixel = int(cnfg.get("arduino","ypixel"))

def open_folder(folder):
    """
        Open a folder using the default file manager
    """
    global is_windows
    if not path.exists(folder) and auto_create_gallery:
        makedirs(folder)
    if path.exists(folder):
        if system() == "Windows" and is_windows:
            startfile(folder)
        elif system() == "Darwin":
            Popen(["open", folder])
        else:
            Popen(["xdg-open", folder])


class GUI(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
        self.connect("activate", self.on_activate)


    def on_activate(self, app):
        self.port = None
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL, application=self)
        self.window.set_title("Camera thermique GUI")
        self.window.set_default_size(300,150)
        self.window.resize(300,150)
        self.window.set_icon_from_file('./images/logo.jpeg')
        self.window.set_resizable(False)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        vbox = Gtk.VBox(spacing=10)
        hbox1 = Gtk.HBox(spacing=10)
        hbox2 = Gtk.HBox(spacing=10)
        # Actions Handler
        mb = Gtk.MenuBar()
        filemenu = Gtk.Menu()
        helpmenu = Gtk.Menu()
        openmenu = Gtk.Menu()
        filem = Gtk.MenuItem("File")
        filem.set_submenu(filemenu)
        helpm = Gtk.MenuItem("Help")
        helpm.set_submenu(helpmenu)
        openfolder = Gtk.MenuItem("Open")

        open_gallery = Gtk.MenuItem("Gallery")
        open_gallery.connect("activate", self.open_gallery)
        open_database = Gtk.MenuItem("Database")
        open_database.connect("activate", self.open_database)
        open_db_file = Gtk.MenuItem("Database file")
        open_db_file.connect("activate", self.open_db_file)
        exit = Gtk.MenuItem("Exit")
        exit.connect("activate", self.quit_application)
        openmenu.append(open_gallery)
        openmenu.append(open_database)
        openmenu.append(open_db_file)
        openfolder.set_submenu(openmenu)
        filemenu.append(openfolder)
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
        vbox.pack_start(mb, False, False ,0)

        # Ports handler
        ports_label = Gtk.Label()
        ports_label.set_text("Port : ")
        ports_label.set_justify(Gtk.Justification.LEFT)
        ports = Gtk.ListStore(str)
        for port in self.get_ports():
            ports.append([port])
        self.window.ports_combo = Gtk.ComboBox.new_with_model(ports)
        self.window.ports_combo.connect("changed", self.on_port_changed)
        renderer_text = Gtk.CellRendererText()
        self.window.ports_combo.pack_start(renderer_text, True)
        self.window.ports_combo.add_attribute(renderer_text, "text", 0)
        self.window.ports_combo.set_active(0)
        hbox1.pack_start(ports_label, False, False, 0)
        hbox1.pack_start(self.window.ports_combo, False, False, 0)
        #Refresh button Handler
        self.window.eventbox = Gtk.EventBox()
        self.window.refresh_button = Gtk.Image()
        self.window.refresh_button.set_from_file("./images/refresh.png")
        self.window.eventbox.add(self.window.refresh_button)
        self.window.eventbox.connect("button-press-event", self.refresh_ports)
        hbox1.pack_start(self.window.eventbox, True, True, 0)
        # Connect Button Handler
        self.window.connect_button = Gtk.Button.new_with_mnemonic("Connect")
        self.window.connect_button.connect("clicked", self.on_connect_clicked)
        hbox1.pack_start(self.window.connect_button, True, True, 0)
        #Message Label
        self.window.label = Gtk.Label()
        self.window.label.set_justify(Gtk.Justification.CENTER)
        self.window.label.set_no_show_all(True)
        #Progress bar
        self.window.start_button = Gtk.Button.new_with_mnemonic("Start")
        self.window.start_button.connect("clicked", self.start_capturing)
        self.window.start_button.set_no_show_all(True)
        self.window.progressbar = Gtk.ProgressBar()
        self.window.progressbar.set_no_show_all(True)
        self.window.progressbar.set_show_text(True)
        self.window.progressbar.set_fraction(0)
        hbox2.pack_start(self.window.start_button, False, False, 0)
        hbox2.pack_start(self.window.progressbar, False, False, 0)
        #Save & show image
        vbox.pack_start(hbox1, False, False, 5)
        vbox.pack_start(self.window.label, False, False, 0 )
        vbox.pack_start(hbox2, False, False, 0)
        self.window.add(vbox)
        self.window.show_all()
        self.add_window(self.window)

    def get_ports(self):
        global is_windows
        ports = []
        if is_windows:
            ports = ['COM%s' % (i + 1) for i in range(256)]
        else:
            for port in comports():
                ports.append(port[0])
        return ports

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
            Update ports lists
        """
        if self.window.ports_combo.get_sensitive():
            ports = Gtk.ListStore(str)
            for port in self.get_ports():
                ports.append([port])
            self.window.ports_combo.set_model(ports)
            self.window.ports_combo.set_active(0)

    def on_connect_clicked(self, button):
        """
            Connect button clicked event handler
        """
        global baud_rate , timeout
        self.window.label.set_text("Connecting..")
        self.window.refresh_button.set_sensitive(True)
        self.window.label.show()
        self.window.connect_button.set_sensitive(False)
        self.window.ports_combo.set_sensitive(False)
        if self.port:
            try :
                self.arduino = serial.Serial(self.port, baud_rate, timeout=timeout)
                if self.arduino.isOpen():
                    self.window.label.hide()
                    self.window.connect_button.set_label("Disconnect")
                    self.window.connect_button.connect("clicked", self.on_disconnect_clicked)
                    self.window.connect_button.set_sensitive(True)
                    self.window.start_button.show()
            except serial.serialutil.SerialException:
                self.window.label.set_text("Could not connect, please try another Port")
                self.window.connect_button.set_sensitive(True)
                self.window.ports_combo.set_sensitive(True)
        else:
            self.window.label.set_text("Please choose a port.")

    def on_disconnect_clicked(self, button):
        """
            Disconnect button clicked event handler
        """
        if self.arduino.isOpen():
            self.arduino.close()
            self.window.label.set_no_show_all(True)
            self.window.label.hide()
            self.window.connect_button.set_sensitive(True)
            self.window.ports_combo.set_sensitive(True)
            self.window.progressbar.hide()
            self.window.start_button.hide()
            self.window.connect_button.set_label("Connect")
            self.window.connect_button.connect("clicked", self.on_connect_clicked)

    def get_temperatures(self):
        self.temperatures = []
        for i in range(1, ypixel + 1):
            line = []
            for j in range(1, xpixel + 1):
                temperature = str(self.arduino.readline())
                temperature = temperature.replace("b'","")
                temperature = temperature.replace(r"\r","")
                if (i-1)%2 == 0:
                    line.append(temperature)
                else:
                    line.insert(0, temperature)
                self.xpixel = j
            self.ypixel = i
            self.temperatures.append(line)

    def start_capturing(self, widget):
        """"
            Start capturing the thermal image
        """
        global date_format, extension, database_folder,\
                xpixel, ypixel
        filename = database_folder + "/" + strftime(date_format,gmtime()) + db_ext
        self.window.start_button.set_sensitive(False)
        self.window.connect_button.set_sensitive(False)
        self.window.progressbar.set_no_show_all(False)
        self.window.progressbar.show()
        self.temperatures = []
        self.xpixel, self.ypixel = 1, 1
        self.arduino.write("start".encode())
        self.thread = threading.Thread(target = self.get_temperatures)
        GObject.timeout_add_seconds(5, self.write_tempertaures, [filename])
        GObject.timeout_add_seconds(0.5, self.update_progressbar)
        self.thread.setDaemon(True)
        self.thread.start()

    def update_progressbar(self):
        global xpixel, ypixel
        fraction = self.window.progressbar.get_fraction()
        if fraction != 1:
            new_value = ((self.ypixel-1)*xpixel + self.xpixel)/(xpixel*ypixel)
            self.window.progressbar.set_fraction(new_value)
            self.window.progressbar.set_text(str(int(new_value*100)) + "%")
            return True
        else:
            self.thread._stop()
            self.window.progressbar.set_text("100%")
            self.window.progressbar.set_fraction(1)
            self.window.progressbar.hide()
            self.window.start_button.set_sensitive(True)
            self.window.connect_button.set_sensitive(True)
            return False

    def write_tempertaures(self, filename):
        global xpixel, ypixel
        if not self.thread.is_alive():
            with open(filename, "wb") as f:
                writer = csv.writer(f)
                writer.writerows(self.temperatures)
            if path.isfile(filename):
                self.show_thermal_image(filename)

    def open_db_file(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        filter = Gtk.FileFilter()
        filter.set_name("Database file")
        filter.add_pattern("*.csv")
        dialog.add_filter(filter)
        response = dialog.run()
        filename = None
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        dialog.destroy()
        if filename:
            threading.Timer(1, self.show_thermal_image(filename))

    def open_gallery(self, widget):
        """"
            Open the gallery folder using the default file manager
        """
        global gallery_folder
        open_folder(gallery_folder)

    def open_database(self, widget):
        """
            Open the database folder using the default file manger
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
            Open the Github repository in the default web browser
        """
        webbrowser.open("https://github.com/archaicmuse/TRANH201-5")

    def show_about(self, widget):
        """
            Show the about dialog
        """
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self.window)
        dialog.set_program_name("Thermal Camera GUI")
        dialog.set_website("https://tranh201groupe5.wordpress.com")
        dialog.set_website_label("Website")
        logo = GdkPixbuf.Pixbuf.new_from_file("./images/logo.jpeg")
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
        dialog.set_version("0.1 Beta")
        dialog.run()
        dialog.destroy()

    def show_thermal_image(self, filename):
        global db_ext, gallery_folder
        f = open(filename)
        lines = f.readlines()
        f.close()
        ypixel = len(lines)
        if ypixel != 0:
            xpixel = len(lines[0].split(","))
            if xpixel != 0:
                data = np.zeros((xpixel, ypixel))
                for i in range(ypixel):
                    line = lines[i].strip().split(",")
                    for j in range(xpixel):
                        data[i,j] = float(line[j])
                plt.clf()
                cmap = get_cmap('jet')
                plt.imshow(data, interpolation="nearest", cmap=cmap)
                plt.axis('off')
                cb = plt.colorbar()
                cb.set_label('Temp (in C)  ')
                database_file = gallery_folder + "/" + path.basename(filename)
                if not path.exists(database_file):
                    plt.savefig(database_file.replace(db_ext ,".png"))
                plt.show()


    def quit_application(self, widget):
        """
            Close the application window
        """
        self.quit()


if __name__ == "__main__":
    app = GUI()
    app.run(None)
