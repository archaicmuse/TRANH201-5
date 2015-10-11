from gi import require_version
from os import path, makedirs
from platform import system
from subprocess import Popen
from time import sleep
require_version('Gtk', '3.0')
from gi.repository import Gtk
try:
    from os import startfile
    is_windows = True
except ImportError:
    is_windows = False

# configurations
gallery_folder = path.split(path.abspath(__file__))[0] + "/gallery"
auto_create_gallery = True


def open_folder(directory):
    """ Opens the directory using the default file manager in OSx,Linux,Windows!
    :param directory: the full path.
    """
    if path.exists(directory):
        if system() == "Windows" and is_windows:
            startfile(path)
        elif system() == "Darwin":
            Popen(["open", path])
        else:
            Popen(["xdg-open", directory])
    else:
        if auto_create_gallery:
            makedirs(directory)


class GUI(Gtk.Window):
    def __init__(self):
        # create the window & set the title
        Gtk.Window.__init__(self, title="Camera thermique GUI")
        self.set_default_size(300,150)
        self.set_border_width(10)
        self.set_resizable(False)

        # create box holder
        # 6 pixels between two child's!
        self.vbox = Gtk.VBox(homogeneous=True, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.hboxbuttons = Gtk.HBox(homogeneous=True, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.hboxbuttons2 = Gtk.HBox(homogeneous=True, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.vboxlabels = Gtk.VBox(homogeneous=True, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.open_gallery = Gtk.Button(label="Open Gallery folder", use_underline=True)
        self.open_gallery.connect("clicked",self.open_gallery_clicked)
        self.open_gallery.set_size_request(20,10)

        self.start_button = Gtk.Button(label= "Start",use_underline=True)
        self.start_button.connect("clicked",self.start_clicked)
        self.start_button.set_size_request(20,10)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_no_show_all(True)
        self.progressbar.hide()

        self.save_button = Gtk.Button(label="Save", use_underline=True)
        self.save_button.connect("clicked", self.save_image)
        self.save_button.set_size_request(20,10)
        self.save_button.set_no_show_all(True)
        self.save_button.hide()

        self.show_button = Gtk.Button(label="Show image", use_underline=True)
        self.show_button.connect("clicked", self.show_image)
        self.show_button.set_size_request(20,10)
        self.show_button.set_no_show_all(True)
        self.show_button.hide()

        self.hboxbuttons.pack_end(self.open_gallery, False, True, 0)
        self.hboxbuttons.pack_end(self.start_button, False, True, 0)
        self.hboxbuttons2.pack_end(self.save_button, False, True, 0)
        self.hboxbuttons2.pack_end(self.show_button, False, True, 0)
        self.vboxlabels.pack_start(self.progressbar, True, True, 0)
        self.vbox.pack_start(self.hboxbuttons, True, True, 6)
        self.vbox.pack_start(self.hboxbuttons2,True, True, 6)
        self.vbox.pack_start(self.vboxlabels, True, True, 6)
        self.add(self.vbox)

    def start_clicked(self, widget):
        self.start_button.set_label("Working!")
        self.start_button.set_sensitive(False)
        self.progressbar.set_no_show_all(False)
        self.progressbar.show()
        self.progressbar.set_fraction(1.0)
        self.progressbar.set_text("Complete 100%")
        self.save_button.set_no_show_all(False)
        self.show_button.set_no_show_all(False)
        self.save_button.show()
        self.show_button.show()
        #self.start_button.set_sensitive(True)
        #self.start_button.set_label("Start")


    def open_gallery_clicked(self, widget):
        open_folder(gallery_folder)

    def show_image(self, widget):
        pass

    def save_image(self, widget):
        pass

win = GUI()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()