from PyQt5.QtWidgets import QTabWidget, QTabBar, QInputDialog

class CustomTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabBar(CustomTabBar(self))

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index != -1:
            self.edit_tab_name(index)
        else:
            super().mouseDoubleClickEvent(event)

    def edit_tab_name(self, index):
        current_name = self.tabText(index)
        new_name, ok = QInputDialog.getText(self, "Edit Tab Name", "New Tab Name:", text=current_name)
        if ok and new_name:
            self.setTabText(index, new_name)
