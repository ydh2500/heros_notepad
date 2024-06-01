import sys
from PyQt5.QtWidgets import QApplication

from py_notepad_widget import NotepadMainWindow


def main():
    app = QApplication(sys.argv)
    main_window = NotepadMainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()