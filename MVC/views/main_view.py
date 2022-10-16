from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot
from PySide6 import QtUiTools
from PySide6.QtCore import *
from BlurWindow.blurWindow import GlobalBlur
from model.PortfolioCustomClasses import DataFrameObject as dfo
#from views.main_view_ui import Ui_MainWindow

class MainView(QWidget):
    def __init__(self, model, list_model, main_controller):
        super().__init__()

        self._model = model
        self._list_model = list_model
        self._main_controller = main_controller

        self._ui = QtUiTools.QUiLoader().load("main_view.ui", self)

        # Overall widget setup for transparency effects
        self._ui.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        GlobalBlur(self.winId(),Acrylic=True,Dark=True,QWidget=self)
        self.setStyleSheet("background-color: rgba(70, 70, 70, 70)")
        self.setWindowTitle('MVC Testing')

        # connect widgets to controller
        self._ui.spinBox_amount.valueChanged.connect(self._main_controller.change_amount)
        self._ui.pushButton_reset.clicked.connect(lambda: self._main_controller.change_amount(0))
        self._ui.lineEdit.textChanged.connect(lambda text = self._ui.lineEdit.text(): self._main_controller.update_name(text))
        self._ui.listWidget.itemClicked.connect(self.send_selected_items)
        self._ui.pushButton_reset_list.clicked.connect(lambda: self._main_controller.change_notepad([]))
        self._ui.pushButton_add_value.clicked.connect(self._main_controller.add_item)

        # listen for model event signals
        self._model.amount_changed.connect(self.on_amount_changed)
        self._model.even_odd_changed.connect(self.on_even_odd_changed)
        self._model.enable_reset_changed.connect(self.on_enable_reset_changed)
        self._list_model.update_name.connect(self.on_update_name)
        self._model.current_selection_changed.connect(self.on_current_selection_changed)
        self._list_model.enable_clear_changed.connect(self.on_enable_clear_changed)
        self._list_model.notepad_changed.connect(self.on_notepad_changed)

        # set a default value
        self._main_controller.change_amount(42)

    # Utility (quasi lambda) functions
    def send_selected_items(self):
        item = self._ui.listWidget.currentItem()
        text = item.text()
        self._main_controller.update_current_selection(text)

    @Slot(dfo)
    def on_current_selection_changed(self, dfo):
        text = f"Selected item: {dfo.oddness}, {str(dfo.value)}, {dfo.name}, {dfo.fish}"
        #''selected item: '+dfo.oddness+', '+dfo.name+', '+dfo.fish
        self._ui.label_dfo_info.setText(text)

    @Slot(int)
    def on_amount_changed(self, value):
        self._ui.spinBox_amount.setValue(value)

    @Slot(str)
    def on_update_name(self, value):
        self._ui.lineEdit.setText(value)

    @Slot(str)
    def on_even_odd_changed(self, value):
        self._ui.label_even_odd.setText(value)

    @Slot(bool)
    def on_enable_reset_changed(self, value):
        self._ui.pushButton_reset.setEnabled(value)

    @Slot(bool)
    def on_enable_clear_changed(self, value):
        self._ui.pushButton_reset_list.setEnabled(value)

    @Slot(list)
    def on_notepad_changed(self, dfolist):
        self._ui.listWidget.clear()
        for dfo in dfolist:
            #print('adding '+i)
            self._ui.listWidget.addItem(dfo.name)
