from PySide6.QtCore import QObject, Slot
from model.PortfolioCustomClasses import DataFrameObject as dfo

class MainController(QObject):
    def __init__(self, model, list_model):
        super().__init__()

        self._model = model
        self._list_model = list_model

    @Slot(int)
    def change_amount(self, value):
        self._model.amount = value

        # calculate even or odd
        self._model.even_odd = 'odd' if value % 2 else 'even'

        # calculate button enabled state
        self._model.enable_reset = True if value else False

    @Slot(str)
    def update_name(self, value):
        self._list_model.name = value

    @Slot(list)
    def change_notepad(self, datalist):
        self._list_model.notepad = datalist

        self._list_model.enable_clear = True if datalist else False

    @Slot(str)
    def add_item(self):
        templist = self._list_model.notepad
        # To do: add error handling
        templist.append(dfo(self._model.even_odd, self._model.amount, self._list_model.name))
        self.change_notepad(templist)

    @Slot(str)
    def update_current_selection(self, text: str): #, _list_model.notepad
        list = self._list_model.notepad
        dfo = self.find_dfo(text, list)
        self._model.current_selection = dfo

    def find_dfo(self, text, list): #symbol, type, filename='na'
        dfo_or_no = next((dfo for dfo in list if dfo.name==text), None)
        return dfo_or_no         
