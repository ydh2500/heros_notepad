import sys
import os
import json
import base64
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QTabWidget, QTabBar, QAction, QFileDialog, QMenu, \
    QInputDialog, QFontComboBox, QToolBar, QComboBox, QToolButton, QMessageBox
from PyQt5.QtGui import QIcon, QImage, QTextCursor, QKeySequence, QFont, QTextDocument, QTextCharFormat, \
    QTextImageFormat
from PyQt5.QtCore import Qt, QBuffer, QByteArray, QUrl


class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HTML Notepad")
        self.setGeometry(100, 100, 800, 600)

        # Initialize Tab Widget
        self.tabs = CustomTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.check_and_close_tab)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.setCentralWidget(self.tabs)

        # Add "탭 추가" Button
        self.add_tab_button = QToolButton(self)
        self.add_tab_button.setIcon(QIcon("icons/add_tab.png"))
        self.add_tab_button.clicked.connect(lambda: self.new_tab("", "New Tab"))
        self.tabs.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)

        # Initialize Toolbars
        self.init_toolbar()

        # Initialize Menu
        self.init_menu()

        # Load or create initial tab
        self.load_or_create_initial_tab()

    def init_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu('File')

        new_action = QAction('New Tab', self)
        new_action.triggered.connect(lambda: self.new_tab("", "New Tab"))
        file_menu.addAction(new_action)

        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

    def init_toolbar(self):
        toolbar = QToolBar("Formatting")
        self.addToolBar(toolbar)

        # Bold action
        bold_action = QAction(QIcon("icons/bold.png"), "Bold", self)
        bold_action.setShortcut(QKeySequence.Bold)
        bold_action.setCheckable(True)
        bold_action.toggled.connect(self.toggle_bold)
        toolbar.addAction(bold_action)

        # Italic action
        italic_action = QAction(QIcon("icons/italic.png"), "Italic", self)
        italic_action.setShortcut(QKeySequence.Italic)
        italic_action.setCheckable(True)
        italic_action.toggled.connect(self.toggle_italic)
        toolbar.addAction(italic_action)

        # Underline action
        underline_action = QAction(QIcon("icons/underline.png"), "Underline", self)
        underline_action.setShortcut(QKeySequence.Underline)
        underline_action.setCheckable(True)
        underline_action.toggled.connect(self.toggle_underline)
        toolbar.addAction(underline_action)

        # Font combo box
        self.font_combobox = QFontComboBox(self)
        self.font_combobox.currentFontChanged.connect(self.change_font)
        self.font_combobox.setCurrentFont(QFont("맑은 고딕"))
        toolbar.addWidget(self.font_combobox)

        # Font size combo box
        self.font_size_combobox = QComboBox(self)
        self.font_size_combobox.setEditable(True)
        self.font_size_combobox.addItems([str(i) for i in range(8, 30)])
        self.font_size_combobox.setCurrentText("12")
        self.font_size_combobox.currentIndexChanged[str].connect(self.change_font_size)
        toolbar.addWidget(self.font_size_combobox)

    def new_tab(self, content="", title="New Tab"):
        editor = CustomTextEdit()
        editor.setHtml(content)
        index = self.tabs.addTab(editor, title)
        self.tabs.setCurrentIndex(index)

    def new_tab_right(self, index):
        self.new_tab()
        self.tabs.tabBar().moveTab(self.tabs.count() - 1, index + 1)

    def new_tab_left(self, index):
        self.new_tab()
        self.tabs.tabBar().moveTab(self.tabs.count() - 1, index)

    def generate_duplicate_title(self, title):
        base_title = title.split('_')[0]
        max_suffix = 1
        for i in range(self.tabs.count()):
            tab_title = self.tabs.tabText(i)
            if tab_title.startswith(base_title):
                parts = tab_title.split('_')
                if len(parts) > 1 and parts[-1].isdigit():
                    suffix = int(parts[-1])
                    if suffix >= max_suffix:
                        max_suffix = suffix + 1
        return f"{base_title}_{max_suffix}"

    def duplicate_tab_right(self, index):
        current_editor = self.tabs.widget(index)
        if isinstance(current_editor, QTextEdit):
            html_content = current_editor.toHtml()
            title = self.tabs.tabText(index)
            new_title = self.generate_duplicate_title(title)
            self.new_tab_right(index)
            new_editor = self.tabs.widget(index + 1)
            new_editor.setHtml(html_content)
            self.tabs.setTabText(index + 1, new_title)

    def duplicate_tab_left(self, index):
        current_editor = self.tabs.widget(index)
        if isinstance(current_editor, QTextEdit):
            html_content = current_editor.toHtml()
            title = self.tabs.tabText(index)
            new_title = self.generate_duplicate_title(title)
            self.new_tab_left(index)
            new_editor = self.tabs.widget(index)
            new_editor.setHtml(html_content)
            self.tabs.setTabText(index, new_title)

    def check_and_close_tab(self, index):
        editor = self.tabs.widget(index)
        if isinstance(editor, QTextEdit):
            if editor.toPlainText().strip():
                reply = QMessageBox.question(self, 'Close Tab',
                                             'This tab contains content. Are you sure you want to close it? This action cannot be undone.',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.close_tab(index)
            else:
                self.close_tab(index)

    def close_tab(self, index):
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.new_tab()

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "HTML Files (*.html);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as file:
                html_content = file.read()
                self.new_tab(html_content, file_name.split('/')[-1])

    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "HTML Files (*.html);;All Files (*)",
                                                   options=options)
        if file_name:
            editor = self.tabs.currentWidget()
            if isinstance(editor, QTextEdit):
                html_content = self.convert_images_to_base64(editor)
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(html_content)

    def show_tab_context_menu(self, position):
        index = self.tabs.tabBar().tabAt(position)
        if index != -1:
            menu = QMenu()

            duplicate_right_action = QAction("Duplicate to the Right", self)
            duplicate_right_action.triggered.connect(lambda: self.duplicate_tab_right(index))
            menu.addAction(duplicate_right_action)

            duplicate_left_action = QAction("Duplicate to the Left", self)
            duplicate_left_action.triggered.connect(lambda: self.duplicate_tab_left(index))
            menu.addAction(duplicate_left_action)

            new_tab_right_action = QAction("New Tab to the Right", self)
            new_tab_right_action.triggered.connect(lambda: self.new_tab_right(index))
            menu.addAction(new_tab_right_action)

            new_tab_left_action = QAction("New Tab to the Left", self)
            new_tab_left_action.triggered.connect(lambda: self.new_tab_left(index))
            menu.addAction(new_tab_left_action)

            close_action = QAction("Close Tab", self)
            close_action.triggered.connect(lambda: self.check_and_close_tab(index))
            menu.addAction(close_action)

            menu.exec_(self.tabs.tabBar().mapToGlobal(position))

    def toggle_bold(self, checked):
        editor = self.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            if checked:
                editor.setFontWeight(QFont.Bold)
            else:
                editor.setFontWeight(QFont.Normal)

    def toggle_italic(self, checked):
        editor = self.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            editor.setFontItalic(checked)

    def toggle_underline(self, checked):
        editor = self.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            editor.setFontUnderline(checked)

    def change_font(self, font):
        editor = self.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            editor.setCurrentFont(font)

    def change_font_size(self, size):
        editor = self.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            editor.setFontPointSize(float(size))

    def closeEvent(self, event):
        self.save_tabs()
        event.accept()

    def save_tabs(self):
        tabs_data = []
        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)
            if isinstance(editor, QTextEdit):
                html_content = self.convert_images_to_base64(editor)
                title = self.tabs.tabText(index)
                tabs_data.append({"title": title, "content": html_content})

        # Save the active tab index
        active_tab_index = self.tabs.currentIndex()

        with open("tabs_data.json", "w", encoding='utf-8') as file:
            json.dump({"active_tab_index": active_tab_index, "tabs": tabs_data}, file, ensure_ascii=False, indent=4)

    def load_tabs(self):
        if os.path.exists("tabs_data.json"):
            with open("tabs_data.json", "r", encoding='utf-8') as file:
                data = json.load(file)
                tabs_data = data.get("tabs", [])
                for tab in tabs_data:
                    self.new_tab(tab["content"], tab["title"])

                # Restore the active tab index
                active_tab_index = data.get("active_tab_index", 0)
                self.tabs.setCurrentIndex(active_tab_index)

    def load_or_create_initial_tab(self):
        if os.path.exists("tabs_data.json"):
            self.load_tabs()
        if self.tabs.count() == 0:
            self.new_tab()

    def convert_images_to_base64(self, editor):
        doc = editor.document()
        html = editor.toHtml()
        image_format = QTextImageFormat()
        cursor = QTextCursor(doc)

        block = doc.begin()
        while block != doc.end():
            block_cursor = QTextCursor(block)
            block_cursor.movePosition(QTextCursor.StartOfBlock)

            while block_cursor.position() < block.position() + block.length() - 1:
                block_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                char_format = block_cursor.charFormat()

                if char_format.isImageFormat():
                    image_format = char_format.toImageFormat()
                    image_name = image_format.name()
                    image_url = QUrl(image_name)
                    image = doc.resource(QTextDocument.ImageResource, image_url)

                    if image is not None:
                        buffer = QBuffer()
                        buffer.open(QBuffer.ReadWrite)
                        image.save(buffer, "PNG")
                        base64_data = base64.b64encode(buffer.data()).decode()
                        new_image_tag = f'<img src="data:image/png;base64,{base64_data}"/>'

                        # Use regex to replace the old image tag with the new one
                        pattern = re.escape(f'<img src="{image_name}"')
                        html = re.sub(pattern + r'([^>]*>)', new_image_tag, html)

                block_cursor.clearSelection()

            block = block.next()

        return html


class CustomTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("맑은 고딕", 12))

    def keyPressEvent(self, event):
        if event == QKeySequence.Paste:
            clipboard = QApplication.clipboard()
            if clipboard.mimeData().hasImage():
                self.paste_image()
            else:
                self.paste()
        else:
            super().keyPressEvent(event)

    def paste_image(self):
        clipboard = QApplication.clipboard()
        if clipboard.mimeData().hasImage():
            image = clipboard.image()
            cursor = self.textCursor()
            cursor.insertImage(image)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        paste_action = menu.addAction("Paste Image")
        paste_action.triggered.connect(self.paste_image)

        if not QApplication.clipboard().mimeData().hasImage():
            paste_action.setEnabled(False)

        menu.exec_(event.globalPos())


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    notepad = Notepad()
    notepad.show()
    sys.exit(app.exec_())
