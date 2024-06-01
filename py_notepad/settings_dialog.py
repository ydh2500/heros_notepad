from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox

try:
    from py_notepad.notepad_data_manager import NotePadDataManager
except ImportError:
    from notepad_data_manager import NotePadDataManager


class SettingsDialog(QDialog):
    def __init__(self, settings, data_manager: NotePadDataManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.data_manager = data_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Serial Label and ComboBox
        self.serial_label = QLabel("Serial:")
        layout.addWidget(self.serial_label)
        self.serial_combobox = QComboBox()
        self.serial_combobox.setEditable(True)
        serials = self.data_manager.get_serials_from_server()
        self.serial_combobox.addItems(serials)

        # 설정에 저장된 serial 값을 선택된 상태로 만듦
        current_serial = self.settings.get("serial", "")
        if current_serial and current_serial not in serials:
            self.serial_combobox.addItem(current_serial)
        self.serial_combobox.setCurrentText(current_serial)

        layout.addWidget(self.serial_combobox)

        # Local File Label and LineEdit
        self.local_file_label = QLabel("Local File:")
        layout.addWidget(self.local_file_label)
        self.local_file_edit = QLineEdit(self.settings.get("local_file", "tabs_data.json"))
        layout.addWidget(self.local_file_edit)

        # Server URL Label and LineEdit
        self.server_url_label = QLabel("Server URL:")
        layout.addWidget(self.server_url_label)
        self.server_url_edit = QLineEdit(self.settings.get("server_url", "http://192.168.5.118:9338"))
        layout.addWidget(self.server_url_edit)

        # Save Button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)
        self.setWindowTitle("Settings")

    def apply_settings(self):
        self.settings["serial"] = self.serial_combobox.currentText()
        if "serials" not in self.settings:
            self.settings["serials"] = []
        if self.settings["serial"] not in self.settings["serials"]:
            self.settings["serials"].append(self.settings["serial"])
        self.settings["local_file"] = self.local_file_edit.text()
        self.settings["server_url"] = self.server_url_edit.text()
        self.accept()
