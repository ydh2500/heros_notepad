from PyQt5.QtWidgets import QToolBar, QAction, QFontComboBox, QComboBox, QColorDialog
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPixmap, QColor

class ToolBar(QToolBar):
    def __init__(self, parent):
        super().__init__("Formatting", parent)
        self.parent = parent
        self.init_toolbar()

    def init_toolbar(self):
        # Bold action
        bold_action = QAction(QIcon(":icons/bold.png"), "Bold", self)
        bold_action.setShortcut(QKeySequence.Bold)
        bold_action.setCheckable(True)
        bold_action.toggled.connect(self.parent.tab_manager.toggle_bold)
        self.addAction(bold_action)

        # Italic action
        italic_action = QAction(QIcon(":icons/italic.png"), "Italic", self)
        italic_action.setShortcut(QKeySequence.Italic)
        italic_action.setCheckable(True)
        italic_action.toggled.connect(self.parent.tab_manager.toggle_italic)
        self.addAction(italic_action)

        # Underline action
        underline_action = QAction(QIcon(":icons/underline.png"), "Underline", self)
        underline_action.setShortcut(QKeySequence.Underline)
        underline_action.setCheckable(True)
        underline_action.toggled.connect(self.parent.tab_manager.toggle_underline)
        self.addAction(underline_action)

        # Font combo box
        self.font_combobox = QFontComboBox(self)
        self.font_combobox.setCurrentFont(QFont("맑은 고딕"))
        self.font_combobox.currentFontChanged.connect(self.parent.tab_manager.change_font)
        self.addWidget(self.font_combobox)

        # Font size combo box
        self.font_size_combobox = QComboBox(self)
        self.font_size_combobox.setEditable(True)
        self.font_size_combobox.addItems([str(i) for i in range(8, 30)])
        self.font_size_combobox.setCurrentText("12")
        self.font_size_combobox.currentIndexChanged[str].connect(self.parent.tab_manager.change_font_size)
        self.addWidget(self.font_size_combobox)

        # Color picker action
        self.color_action = QAction(QIcon(), "Text Color", self)
        self.update_text_color_icon(QColor("black"))
        self.color_action.triggered.connect(self.parent.tab_manager.select_text_color)
        self.addAction(self.color_action)

        # Save action
        save_action = QAction(QIcon(":icons/save.png"), "Save", self)
        save_action.triggered.connect(self.parent.file_manager.save_tabs)
        self.addAction(save_action)

        # Refresh action
        refresh_action = QAction(QIcon(":icons/refresh.png"), "Refresh", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.parent.tab_manager.refresh_tabs)
        self.addAction(refresh_action)

    def update_text_color_icon(self, color):
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        self.color_action.setIcon(QIcon(pixmap))
