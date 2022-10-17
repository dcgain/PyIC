import sys
from PySide6.QtWidgets import QApplication
from model.model import Model
from model.list_model import List_Model
from controllers.main_ctrl import MainController
from views.main_view import MainView
import qdarktheme

class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.model = Model()
        self.list_model = List_Model()
        self.main_controller = MainController(self.model,self.list_model)
        self.main_view = MainView(self.model, self.list_model, self.main_controller)
        self.main_view.show()

        self.setStyleSheet(qdarktheme.load_stylesheet()) 

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec())