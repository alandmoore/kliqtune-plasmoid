from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon
from PyQt4.QtCore import Qt


class LauncherButton(Plasma.ToolButton):
    def __init__(self, launcher=None):
        self.launcher = launcher
        Plasma.ToolButton.__init__(self)
        self.icon = ((self.launcher.icon is not None) and KIcon(self.launcher.icon)) or KIcon()
        self.setText("  %s  " % self.launcher.button_text)
        self.tooltip_data = Plasma.ToolTipContent(launcher.button_text, launcher.tooltip_text, self.icon)
        self.tooltip_data.setAutohide(False)
        self.updateGeometry()

    def activate(self):
        #called when the button is active
        self.setText("<<%s>>" % self.launcher.button_text)
        self.nativeWidget().setDown(True)

    def deactivate(self):
        #called when the button is released
        self.setText("  %s  " % self.launcher.button_text)
        self.nativeWidget().setDown(False)
        
    def update_tooltip_metadata(self, metadata_string):
        self.tooltip_data = Plasma.ToolTipContent(self.launcher.button_text, "\n".join([self.launcher.tooltip_text, metadata_string]), self.icon)
        self.tooltip_data.setAutohide(False)
        Plasma.ToolTipManager.self().setContent(self, self.tooltip_data)
