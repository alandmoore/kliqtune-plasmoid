from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.kio import KIconButton
from PyKDE4.kio import KFileDialog
from PyKDE4.kdecore import KUrl

from launcher_config_ui import Ui_Form
from launcher import Launcher


class Launcher_Config(QWidget, Ui_Form):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent
        self.setupUi(self)
        self.launchers = parent.launchers
        self.launchers.reverse()
        #populate the table
        for launcher in self.launchers:
            self.tableWidget.insertRow(0)
            self.tableWidget.setCellWidget(0, 0, KIconButton())
            if launcher.icon is not None:
                self.tableWidget.cellWidget(0,0).setIcon(launcher.icon)
            self.tableWidget.setItem(0, 1, QTableWidgetItem(launcher.button_text))
            self.tableWidget.setItem(0, 2, QTableWidgetItem(launcher.media_url))
            self.tableWidget.setItem(0, 3, QTableWidgetItem(launcher.tooltip_text))
            self.connect(self.tableWidget.cellWidget(0,0), SIGNAL("iconChanged(QString)"), self.tableWidget.resizeRowsToContents)
        self.tableWidget.resizeRowsToContents()

        self.connect(self.add_button, SIGNAL("clicked()"), self.newRow)
        self.connect(self.remove_button, SIGNAL("clicked()"), self.killRow)
        self.connect(self.tableWidget, SIGNAL("itemSelectionChanged()"), self.toggle_selection_specific_buttons)
        self.connect(self.move_up_button, SIGNAL("clicked()"), self.move_row_up)
        self.connect(self.move_down_button, SIGNAL("clicked()"), self.move_row_down)
        self.connect(self.export_button, SIGNAL("clicked()"), self.export_to_file)

    def newRow(self):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        self.tableWidget.setCellWidget((self.tableWidget.rowCount() -1),0, KIconButton())

    def killRow(self):
        self.tableWidget.removeRow(self.tableWidget.currentRow())

    def get_launcher_list(self):
        launchers = []
        for rownum in range(self.tableWidget.rowCount()):
            display_rownum = int(rownum) + 1
            icon = self.tableWidget.cellWidget(rownum, 0) and unicode(self.tableWidget.cellWidget(rownum, 0).icon())
            if icon == "":
                icon = None
            button_text = self.tableWidget.item(rownum, 1) and unicode(self.tableWidget.item(rownum, 1).text())
            media_url = self.tableWidget.item(rownum, 2) and unicode(self.tableWidget.item(rownum, 2).text())
            tooltip_text = (self.tableWidget.item(rownum, 3) and unicode(self.tableWidget.item(rownum, 3).text())) or ""
            if (button_text is not None and  media_url is not None):
               launchers.append(Launcher(button_text, media_url, tooltip_text, icon))
            else:
                KMessageBox.error(None, "Launcher #%d could not be added, because it was missing the button text or media URL." % display_rownum, "Error adding launcher")

        return launchers

    def toggle_selection_specific_buttons(self):
        enable = len(self.tableWidget.selectedItems()) > 0
        up_enable = self.tableWidget.currentRow() > 0
        down_enable = (self.tableWidget.currentRow() + 1) < self.tableWidget.rowCount()
        self.remove_button.setEnabled(enable)
        self.move_up_button.setEnabled(enable and  up_enable)
        self.move_down_button.setEnabled(enable and down_enable)
    
    def move_row_up(self):
        source = self.tableWidget.currentRow()
        destination = source - 1
        self.row_swap(source, destination)
    def move_row_down(self):
        source = self.tableWidget.currentRow()
        destination = source + 1
        self.row_swap(source, destination)

    def row_swap(self, source, destination):
        for field in range(self.tableWidget.columnCount()):
            item = self.tableWidget.takeItem(source, field)
            self.tableWidget.setItem(source, field, self.tableWidget.takeItem(destination, field))
            self.tableWidget.setItem(destination, field, item)
        self.tableWidget.setCurrentCell(destination, self.tableWidget.currentColumn())

    def export_to_file(self):
        filename = KFileDialog.getSaveFileName(KUrl("~"), "Text (*.txt)", self, "Select file to save launcher data")
        fh = open(filename, 'w')
        for rownum in range(self.tableWidget.rowCount()):
            icon = self.tableWidget.cellWidget(rownum, 0) and unicode(self.tableWidget.cellWidget(rownum, 0).icon()) or ""
            button_text = self.tableWidget.item(rownum, 1) and unicode(self.tableWidget.item(rownum, 1).text())
            media_url = self.tableWidget.item(rownum, 2) and unicode(self.tableWidget.item(rownum, 2).text())
            tooltip_text = (self.tableWidget.item(rownum, 3) and unicode(self.tableWidget.item(rownum, 3).text())) or ""
            if button_text and media_url:
                fh.write("\t".join([icon, button_text, media_url, tooltip_text]) + "\n")
        fh.close()
