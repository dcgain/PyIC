from PySide6.QtCore import QObject, Signal
from model.PortfolioCustomClasses import DataFrameObject as dfo
#from model.CounterClass import CounterClass as ccl

class Model(QObject):
    amount_changed = Signal(int)
    even_odd_changed = Signal(str)
    enable_reset_changed = Signal(bool)
    current_selection_changed = Signal(dfo)

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value
        self.amount_changed.emit(value)

    @property
    def even_odd(self):
        return self._even_odd

    @even_odd.setter
    def even_odd(self, value):
        self._even_odd = value
        self.even_odd_changed.emit(value)

    @property
    def current_selection(self):
        return self._current_selection

    @current_selection.setter
    def current_selection(self, value: dfo):
        self._current_selection = value
        self.current_selection_changed.emit(value)

    @property
    def enable_reset(self):
        return self._enable_reset

    @enable_reset.setter
    def enable_reset(self, value):
        self._enable_reset = value
        self.enable_reset_changed.emit(value)

    def __init__(self):
        super().__init__()

        self._amount = 0
        self._even_odd = ''
        self._enable_reset = False
        self._current_selection = dfo('odd',1,'name')