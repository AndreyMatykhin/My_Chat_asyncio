from PyQt5 import QtWidgets
from client.ui.login_ui import Ui_Login_Dialog as login_ui_class
from client.ui.contacts_ui import Ui_ContactsWindow as contacts_ui_class

class LoginWindow(QtWidgets.QDialog):
    """Login Window (user interface)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = login_ui_class()
        self.ui.setupUi(self)


class ContactsWindow(QtWidgets.QMainWindow):
    """Contacts Window (user interface)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        super.ui = contacts_ui_class()
        super.ui.setupUi(self)
