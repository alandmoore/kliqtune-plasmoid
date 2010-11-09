# -*- coding: utf-8 -*-
##TinyTune##
# A simple media player intended for audio streams
# for people who just want their favorite streams a click away
# By Alan D Moore http://www.alandmoore.com (me at alan d moore dot com)
# Released under the terms of the GNU GPL2 or later
# see the included "COPYING" file for details.


import pickle

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4 import kdeui
from PyQt4.phonon import Phonon

from launcherConfig import Launcher_Config
from launcher import Launcher
from launcherButton import LauncherButton
from appearanceConfig import Appearance_Config

class KliQTune(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
        self.default_launchers = pickle.dumps([
                Launcher("The WIR", "http://74.112.209.3/stream", "WYIR, Evansville, IN.  This plugin was built for streams, like this one."),
                Launcher("Lykwyd Chykyn", "http://www.alandmoore.com/lc/aud/m3u.php", "You can also play M3U files on the web, or locally.  Here's some random music from Alan D. Moore, the author of this plasma widget."),
                Launcher("CD", "cdda:/", "You can play Compact Discs too!  Just put the disc in, wait for it to spin up, then click this button.", "media-optical-audio")
                ])
        self.mylayout = None
        self.parent=parent
        self.buttons = []

    def init(self):
        self.setHasConfigurationInterface(True)
        #Get configuration
        self.configuration = self.config()
        self.launchers = str(self.configuration.readEntry("launchers", self.default_launchers).toString())
        self.launchers = pickle.loads(self.launchers)
        self.use_fixed_width = (self.configuration.readEntry("use_fixed_width", False).toBool())
        self.fixed_width = self.configuration.readEntry("fixed_width", 100).toInt()[0]
        self.layout_orientation = self.configuration.readEntry("layout_orientation", Qt.Horizontal).toInt()[0]
        self.background_type = self.configuration.readEntry("background_type", "default").toString()
        self.show_volume = (self.configuration.readEntry("show_volume", True).toBool())
        self.last_volume = (self.configuration.readEntry("last_volume", 75).toInt())[0]
        self.use_icons = (self.configuration.readEntry("use_icons", True).toBool())
        print self.fixed_width
        
        #basic setup
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.set_background()
        self.media_object = Phonon.MediaObject(self)
        self.active_button= None
        self.audio_out = Phonon.AudioOutput(Phonon.MusicCategory, self)
        #Add the widgets to the layout
        self.refresh_launchers()
        self.setLayout(self.mylayout)
        self.volume_change(self.last_volume)
        
        self.connect(self.media_object, SIGNAL("metaDataChanged()"), self.update_metadata)
        Phonon.createPath(self.media_object, self.audio_out)

    def createConfigurationInterface(self, parent):
        self.launchers_config = Launcher_Config(self)
        p = parent.addPage(self.launchers_config, "Launchers")
        p.setIcon(kdeui.KIcon("preferences-other"))

        self.appearance_config = Appearance_Config(self)
        p2 = parent.addPage(self.appearance_config, "Appearance")
        p2.setIcon(kdeui.KIcon("preferences-color"))
        self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
        self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)

    def showConfigurationInterface(self):
        self.dialog = kdeui.KPageDialog()
        self.dialog.setFaceType(kdeui.KPageDialog.List)
        self.dialog.setButtons(kdeui.KDialog.ButtonCode(kdeui.KDialog.Ok |kdeui.KDialog.Cancel))
        self.createConfigurationInterface(self.dialog)
        self.dialog.resize(800, 500)
        self.dialog.show()

    def configAccepted(self):
        self.launchers = self.launchers_config.get_launcher_list()
        self.use_fixed_width = self.appearance_config.get_use_fixed_width()
        self.fixed_width = self.appearance_config.get_fixed_width()
        self.layout_orientation = self.appearance_config.get_layout_orientation()
        self.background_type = self.appearance_config.get_background_type()
        self.show_volume = self.appearance_config.get_show_volume()
        self.use_icons = self.appearance_config.get_use_icons()

        self.refresh_launchers()
        self.set_background()
        #save data
        self.configuration.writeEntry("launchers", QVariant(pickle.dumps(self.launchers)))
        self.configuration.writeEntry("use_fixed_width", QVariant(self.use_fixed_width))
        self.configuration.writeEntry("fixed_width", QVariant(self.fixed_width))
        self.configuration.writeEntry("layout_orientation", QVariant(self.layout_orientation))
        self.configuration.writeEntry("background_type", QVariant(self.background_type))
        self.configuration.writeEntry("show_volume", QVariant(self.show_volume))
        self.configuration.writeEntry("use_icons", QVariant(self.use_icons))

    def configDenied(self):
        pass

    def set_background(self):
        if self.background_type == QString("translucent"):
            self.setBackgroundHints(Plasma.Applet.TranslucentBackground)
        else:
            self.setBackgroundHints(Plasma.Applet.DefaultBackground)

    def create_volume_slider(self):
        self.volume_slider = Plasma.Slider()
        self.volume_slider.setOrientation(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.last_volume)
        if self.use_fixed_width and self.layout_orientation == Qt.Vertical:
            self.volume_slider.nativeWidget().setFixedWidth(self.fixed_width)
        self.volume_tooltip = Plasma.ToolTipContent("Volume", "%d %%"% self.audio_out.volume(), QIcon()) 
        Plasma.ToolTipManager.self().setContent(self.volume_slider, self.volume_tooltip)
        self.connect(self.volume_slider, SIGNAL("valueChanged(int)"), self.volume_change)
        self.connect(self.audio_out, SIGNAL("volumeChanged(float)"), self.change_slider)

    def refresh_launchers(self):
        if self.mylayout:
            self.remove_buttons()
        self.mylayout = QGraphicsLinearLayout(self.layout_orientation, self.applet)
        if self.show_volume:
            self.create_volume_slider()
            self.mylayout.addItem(self.volume_slider)
        self.buttons = []
        for a_launcher in self.launchers:
            self.buttons.append(LauncherButton(a_launcher))

            #Tooltips
            self.buttons[-1].update_tooltip_metadata("")

            #fixed width or not:
            if self.use_fixed_width:
                self.buttons[-1].nativeWidget().setFixedWidth(self.fixed_width)
            #icon, if set
            if a_launcher.icon is not None and self.use_icons:
                self.buttons[-1].setIcon(kdeui.KIcon(a_launcher.icon))
            #connect and add
            self.connect(self.buttons[-1], SIGNAL("clicked()"), self.play)
            self.mylayout.addItem(self.buttons[-1])
            
        #Add off button
        self.offbutton = Plasma.ToolButton()
        self.offbutton.setText("  Off  ")
        Plasma.ToolTipManager.self().setContent(self.offbutton, Plasma.ToolTipContent("Off", "Stop the music!", kdeui.KIcon("media-playback-stop")))
        if self.use_fixed_width:
            self.offbutton.nativeWidget().setFixedWidth(self.fixed_width)
        if self.use_icons:
            self.offbutton.setIcon(kdeui.KIcon("media-playback-stop"))
        self.connect(self.offbutton, SIGNAL("clicked()"), self.stop)
        self.mylayout.addItem(self.offbutton)

        self.mylayout.setContentsMargins(0,0,0,0)
        
    def remove_buttons(self):
        while self.mylayout.count() != 0:
            self.mylayout.removeItem(self.mylayout.itemAt(0))
    
    def play(self):
        self.stop()
        self.active_button = self.sender()
        m_url = self.active_button.launcher.media_url
        self.active_button.update_tooltip_metadata("<br /><i>Loading...</i>")
        self.active_button.activate()
        self.media_object.setCurrentSource(Phonon.MediaSource(m_url))
        self.media_object.play()

    def stop(self):
        for button in self.buttons:
            button.deactivate()
            button.update_tooltip_metadata("")
        self.media_object.stop()

    def volume_change(self, volume):
        """volume is an integer from 0 to 100."""
        self.audio_out.setVolume(float(volume)/100.0)
        if self.show_volume:
            self.volume_tooltip.setSubText("%d %%" % volume)
            Plasma.ToolTipManager.self().setContent(self.volume_slider, self.volume_tooltip)
            Plasma.ToolTipManager.self().show(self.volume_slider)
        self.configuration.writeEntry("last_volume", QVariant(volume))
    def change_slider(self, volume_percent):
        self.volume_tooltip.setSubText("%d %%" % volume_percent * 100)
        Plasma.ToolTipManager.self().setContent(self.volume_slider, self.volume_tooltip)
        self.volume_slider.setValue(volume_percent * 100)

    def update_metadata(self):
        metadata = self.media_object.metaData()
        output = ""
        for key, data in metadata.iteritems():
            if data != [QString("")]:
                output += "<br />%s:  %s" % (key, data[0])
        self.active_button.update_tooltip_metadata(output)


def CreateApplet(parent):
    return KliQTune(parent)
