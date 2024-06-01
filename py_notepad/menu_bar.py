from PyQt5.QtWidgets import QMenuBar, QAction
from PyQt5.QtGui import QKeySequence


class MenuBar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_menu()

    def init_menu(self):
        # File Menu
        file_menu = self.addMenu('File')

        new_action = QAction('New Tab', self)
        new_action.triggered.connect(lambda: self.parent.new_tab("", "New Tab"))
        file_menu.addAction(new_action)

        open_action = QAction('Open', self)
        open_action.triggered.connect(self.parent.file_manager.open_file)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.parent.file_manager.save_tabs)
        file_menu.addAction(save_action)
