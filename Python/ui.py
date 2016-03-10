#!/usr/bin/python3
from gi import require_version
from os import path, makedirs, stat
from platform import system
from subprocess import Popen
from configparser import ConfigParser, RawConfigParser
import serial
import serial.tools.list_ports
from time import sleep, strftime, gmtime
from matplotlib import use
use('GTK3Agg')
from pylab import get_cmap
import glob
import matplotlib.pyplot as plt
import numpy as np
from csv import writer
from threading import Thread
from re import findall
require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, Gdk
try:
    from os import startfile
    is_windows = True
except ImportError:
    is_windows = False
""" TODO :
 - > 1000°C
"""
# configurations
GObject.threads_init()
cnfg = ConfigParser()
cnfg.read("settings.ini")
absolute_path = path.split(path.abspath(__file__))[0] + "/"
database_folder = absolute_path + cnfg.get("database", "folder")
gallery_folder = absolute_path + cnfg.get("gallery", "folder")
db_ext = "." + cnfg.get("database", "extension")
date_format = "%d-%m-%Y_%H-%M-%S"
baud_rate = int(cnfg.get("arduino", "baud_rate"))
timeout = float(cnfg.get("arduino", "timeout"))
xpixel = int(cnfg.get("arduino", "xpixel"))
ypixel = int(cnfg.get("arduino", "ypixel"))
unit_temperature = str(cnfg.get("gallery", "units")).upper()
temperature_units = ["K", "C", "F"]



def open_folder(folder):
    """
        Open a folder using the default file manager
    """
    global is_windows
    if not path.exists(folder):
        makedirs(folder)
    if path.exists(folder):
        if system() == "Windows" and is_windows:
            startfile(folder)
        elif system() == "Darwin":
            Popen(["open", folder])
        else:
            Popen(["xdg-open", folder])


def convert_temperature(temperature, unit):
    """
        The temperature by default is on °C
        Args:
            @temperature (float) : the temperature
            @unit (str): the unit to convert to, C , F and K
    """
    if unit == "C":
        return temperature
    elif unit == "K":
        return temperature + 273.15
    elif unit == "F":
        return (temperature * 9 / 5 + 32)


class GUI(Gtk.Application):
    data = []

    def __init__(self, xpixel, ypixel):
        Gtk.Application.__init__(self)
        self.data = np.zeros((xpixel, ypixel))
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.port = None
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL, application=self)
        self.window.set_wmclass("Camera thermique GUI", "Camera thermique GUI")
        self.window.set_title("Camera thermique GUI")
        self.window.set_default_size(300, 150)
        self.window.resize(300, 150)
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
        settings = Gtk.MenuItem("Settings")
        settings.connect("activate", self.open_settings)
        exit = Gtk.MenuItem("Exit")
        exit.connect("activate", lambda x: self.quit())
        openmenu.append(open_gallery)
        openmenu.append(open_database)
        openmenu.append(open_db_file)
        openfolder.set_submenu(openmenu)
        filemenu.append(openfolder)
        filemenu.append(settings)
        filemenu.append(exit)

        about_menu = Gtk.MenuItem("About")
        about_menu.connect("activate", self.show_about)
        helpmenu.append(about_menu)
        mb.append(filem)
        mb.append(helpm)
        vbox.pack_start(mb, False, False, 0)
        # Ports handler
        ports_label = Gtk.Label()
        ports_label.set_text("Port : ")
        ports_label.set_margin_left(10)
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
        # Refresh button Handler
        self.window.eventbox = Gtk.EventBox()
        self.window.refresh_button = Gtk.Image()
        self.window.refresh_button.set_from_file("./images/refresh.png")
        self.window.eventbox.add(self.window.refresh_button)
        self.window.eventbox.connect("button-press-event", self.refresh_ports)
        hbox1.pack_start(self.window.eventbox, True, True, 0)
        # Connect Button Handler
        self.window.connect_button = Gtk.Button.new_with_mnemonic("Connect")
        self.window.connect_button.connect("clicked", self.on_connect_clicked)
        self.window.connect_button.set_margin_right(10)
        hbox1.pack_start(self.window.connect_button, True, True, 0)
        # Message Label
        self.window.label = Gtk.Label()
        self.window.label.set_justify(Gtk.Justification.CENTER)
        self.window.label.set_no_show_all(True)
        # Progress bar
        self.window.start_button = Gtk.Button.new_with_mnemonic("Start")
        self.window.start_button.connect("clicked", self.start_capturing)
        self.window.start_button.set_margin_left(10)
        self.window.start_button.set_margin_bottom(10)
        self.window.start_button.set_no_show_all(True)
        self.window.progressbar = Gtk.ProgressBar()
        self.window.progressbar.set_margin_right(10)
        self.window.progressbar.set_margin_left(20)
        self.window.progressbar.set_margin_bottom(20)
        self.window.progressbar.set_no_show_all(True)
        self.window.progressbar.set_show_text(True)
        self.window.progressbar.set_fraction(0)
        hbox2.pack_start(self.window.start_button, False, False, 0)
        hbox2.pack_start(self.window.progressbar, False, False, 0)
        # Save & show image
        vbox.pack_start(hbox1, False, False, 5)
        vbox.pack_start(self.window.label, False, False, 0)
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
            ports = []
            for port in glob.glob('/dev/tty[A-Za-z]*'):
                ports.append(port)
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

    def refresh_ports(self, eventbox, button):
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
        global baud_rate, timeout
        self.window.label.set_text("Connecting..")
        self.window.refresh_button.set_sensitive(True)
        self.window.label.show()
        self.window.connect_button.set_sensitive(False)
        self.window.ports_combo.set_sensitive(False)
        if self.port:
            try:
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
        f = open(self.filename, "w")
        cwriter = writer(f, delimiter=",")
        database_file = gallery_folder + "/" + path.basename(self.filename)

        for i in range(1, ypixel + 1):
            line = []
            for j in range(1, xpixel + 1):
                temperature = self.arduino.readline().strip().decode()
                temperature = float(temperature) if temperature else 0.0
                print(temperature)
                # just for tests!
                line.append(temperature)
                self.data[i - 1, j - 1] = convert_temperature(temperature, unit_temperature)
                self.xpixel = j if j != xpixel else 0
            self.ypixel = i
            if len(line) == xpixel:
                cwriter.writerow(line)
        f.close()
        if not path.exists(database_file):
            plt.savefig(database_file.replace(db_ext, ".png"))
        return False

    def start_capturing(self, widget):
        """"
            Start capturing the thermal image
        """
        global date_format, extension, database_folder,\
            xpixel, ypixel
        self.filename = database_folder + "/" + strftime(date_format, gmtime()) + db_ext
        self.window.start_button.set_sensitive(False)
        self.window.connect_button.set_sensitive(False)
        self.window.progressbar.set_no_show_all(False)
        self.window.progressbar.show()
        self.xpixel, self.ypixel = 0, 0
        self.arduino.write("start".encode())
        fig = plt.figure()
        plt.autoscale(True)
        plt.clf()
        cmap = get_cmap('jet')
        self.img = plt.imshow(self.data, interpolation="nearest", cmap=cmap,  aspect='auto')
        plt.axis('off')
        self.cb = fig.colorbar(self.img)
        self.cb.set_label("Temperature (°" + unit_temperature.upper() + ")  ")
        thread = Thread(target=plt.show)
        thread.setDaemon(True)
        thread.start()
        GObject.timeout_add_seconds(1, self.update_progressbar)
        self.thread = Thread(target=self.get_temperatures)
        self.thread.setDaemon(True)
        self.thread.start()

    def update_progressbar(self):
        global xpixel, ypixel
        fraction = self.window.progressbar.get_fraction()
        if fraction != 1:
            new_value = ((self.ypixel) * xpixel + self.xpixel) / (xpixel * ypixel)
            self.window.progressbar.set_fraction(new_value)
            self.window.progressbar.set_text(str(int(new_value * 100)) + "%")
            self.img.set_data(self.data)
            self.cb.set_clim(vmax=self.data.max(),vmin=self.data.min())
            self.img.changed()
            plt.autoscale()
            plt.draw()
            return True
        else:
            self.window.progressbar.set_fraction(0)
            self.window.progressbar.set_text(str("0%"))
            self.window.progressbar.hide()
            self.window.start_button.set_sensitive(True)
            self.window.connect_button.set_sensitive(True)
            return False
    
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
        filename = dialog.get_filename()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            self.show_thermal_image(filename)

    def choose_folder(self, *args):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_action(Gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        response = dialog.run()
        foldername = dialog.get_filename()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return foldername

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

    def show_about(self, widget):
        """
            Show the about dialog
        """
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self.window)
        dialog.set_program_name("Thermal Camera GUI")
        dialog.set_website("https://github.com/archaicmuse/TRANH201-5")
        dialog.set_website_label("Github repository")
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
        global db_ext, gallery_folder, unit_temperature
        if path.isfile(filename):
            f = open(filename)
            lines = f.readlines()
            f.close()
            if not self.file_is_empty(filename):
                ypixel = len(lines)
                xpixel = len(lines[0].split(","))
                data = np.zeros((xpixel, ypixel))
                for i in range(ypixel):
                    line = lines[i].strip().split(",")
                    for j in range(xpixel):
                        data[i, j] = convert_temperature(float(line[j]), unit_temperature)
                fig = plt.figure()
                plt.clf()
                cmap = get_cmap('jet')
                plt.imshow(data, interpolation="nearest", cmap=cmap)
                plt.axis('off')
                cb = plt.colorbar()
                cb.set_label("Temperature (°" + unit_temperature.upper() + ")  ")
                plt.show()
            else:
                self.show_notification("Please choose an other file", "The file seems to be empty or corrupted")
        else:
            self.show_notification("Please choose an other file", "Please choose a file instead of a folder")

    def show_notification(self, title, message):
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(message)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dialog.destroy()

    def open_settings(self, *args):
        cnfg = ConfigParser()
        cnfg.read("settings.ini")
        self.swin = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.swin.set_transient_for(self.window)
        self.swin.set_position(Gtk.WindowPosition.CENTER)
        self.swin.set_title("Settings")
        self.swin.set_resizable(False)
        self.swin.connect("delete-event", lambda x, y: self.swin.destroy())
        self.swin.set_border_width(10)
        self.swin.set_default_size(200, 100)
        self.swin.resize(200, 100)
        vbox = Gtk.VBox(spacing=10)

        hbox4 = Gtk.HBox(spacing=5)
        temperature_label = Gtk.Label("Temperature unit : ")
        units = Gtk.ListStore(str)
        id_active = 0
        i = 0
        for unit in temperature_units:
            if unit.upper() == cnfg.get("gallery", "units").upper():
                id_active = i
            units.append([unit])
            i += 1
        self.temperature_entry = Gtk.ComboBox.new_with_model(units)
        renderer_text = Gtk.CellRendererText()
        self.temperature_entry.pack_start(renderer_text, True)
        self.temperature_entry.add_attribute(renderer_text, "text", 0)

        self.temperature_entry.set_active(id_active)
        hbox4.pack_start(temperature_label, False, False, 0)
        hbox4.pack_end(self.temperature_entry, False, False, 0)
        hbox5 = Gtk.HBox(spacing=5)
        resolution_label = Gtk.Label("Image resolution : ")
        xlabel = Gtk.Label("X")
        self.xpixel_entry = Gtk.Entry()
        self.xpixel_entry.set_text(cnfg.get("arduino", "xpixel"))
        self.xpixel_entry.set_max_length(3)
        self.xpixel_entry.set_max_width_chars(3)
        self.xpixel_entry.set_width_chars(3)
        self.ypixel_entry = Gtk.Entry()
        self.ypixel_entry.set_text(cnfg.get("arduino", "ypixel"))
        self.ypixel_entry.set_max_length(3)
        self.ypixel_entry.set_max_width_chars(3)
        self.ypixel_entry.set_width_chars(3)
        hbox5.pack_start(resolution_label, False, False, 0)
        hbox5.pack_end(self.ypixel_entry, False, False, 0)
        hbox5.pack_end(xlabel, False, False, 0)
        hbox5.pack_end(self.xpixel_entry, False, False, 0)

        hbox_buttons = Gtk.HBox(spacing=5)
        apply_button = Gtk.Button("Apply")
        apply_button.connect("clicked", self.save_settings)
        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect("clicked", lambda x: self.swin.destroy())
        hbox_buttons.pack_end(apply_button, False, False, 0)
        hbox_buttons.pack_end(cancel_button, False, False, 0)

        vbox.pack_start(hbox4, False, False, 0)
        vbox.pack_start(hbox5, False, False, 0)
        vbox.pack_start(hbox_buttons, True, True, 0)
        self.swin.add(vbox)
        self.swin.show_all()

    def file_is_empty(self, filename):
        return (stat(filename).st_size == 0)

    def save_settings(self, *args):
        config = RawConfigParser()
        config.read("settings.ini")
        config.set("arduino", "xpixel", str(int(self.xpixel_entry.get_text())))
        config.set("arduino", "ypixel", str(int(self.ypixel_entry.get_text())))

        tree_iter = self.temperature_entry.get_active_iter()
        if tree_iter:
            model = self.temperature_entry.get_model()
            temperature_unit = model[tree_iter][0]
        config.set("gallery", "units", temperature_unit)
        configfile = open("settings.ini",  "w")
        config.write(configfile)
        configfile.close()
        self.swin.destroy()

if __name__ == "__main__":
    app = GUI(xpixel, ypixel)
    app.run(None)
