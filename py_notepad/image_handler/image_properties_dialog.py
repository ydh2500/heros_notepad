from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QComboBox

class ImagePropertiesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Image Properties')

        self.layout = QFormLayout(self)

        self.scale_input = QComboBox(self)
        self.scale_input.addItems(["50%", "75%", "100%", "125%", "150%", "200%"])
        self.scale_input.setCurrentText("100%")
        self.layout.addRow('Scale:', self.scale_input)

        self.title_input = QLineEdit(self)
        self.layout.addRow('Title:', self.title_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_properties(self):
        scale_text = self.scale_input.currentText()
        scale = float(scale_text.strip('%')) / 100.0
        return scale, self.title_input.text()
