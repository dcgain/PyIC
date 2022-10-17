from PySide6.QtCore import QObject, Signal
from model.PortfolioCustomClasses import DataFrameObject as dfo

class List_Model(QObject):
    notepad_changed = Signal(list)
    item_qty_changed = Signal(int)
    list_cleared = Signal(bool)
    enable_clear_changed = Signal(bool)
    update_name = Signal(str)

    @property
    def notepad(self):
        return self._notepad

    @notepad.setter
    def notepad(self, list):
        self._notepad = list
        self.notepad_changed.emit(list)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, namestring):
        self._name = namestring
        self.update_name.emit(namestring)

    @property
    def item_qty(self):
        return self._even_odd

    @item_qty.setter
    def item_qty(self, value):
        self._find_list_length = value
        self.item_qty_changed.emit(value)

    @property
    def enable_clear(self):
        return self._enable_clear

    @enable_clear.setter
    def enable_clear(self, value):
        self._enable_clear = value
        self.enable_clear_changed.emit(value)


    def __init__(self):
        super().__init__()

        self._item_qty = 0 #start with zero list items
        self._enable_clear = False
        self._notepad = [] #empty list of dfo
        self._name = 'name'