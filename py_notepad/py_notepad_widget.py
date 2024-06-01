import sys
import json
import base64
import re
from datetime import datetime

import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QTabWidget, QTabBar, QAction, QFileDialog, QMenu, QInputDialog, QFontComboBox, QToolBar, QComboBox, QToolButton, QMessageBox, QVBoxLayout, QWidget, QMenuBar, QColorDialog
from PyQt5.QtGui import QIcon, QTextCursor, QKeySequence, QFont, QTextDocument, QTextCharFormat, QTextImageFormat, QColor, QPixmap
from PyQt5.QtCore import Qt, QBuffer, QByteArray, QUrl, QTimer

try:
    from py_notepad.notepad_data_manager import NotePadDataManager
except ImportError:
    from notepad_data_manager import NotePadDataManager

try:
    from py_notepad import resources_rc
except ImportError:
    import resources_rc

class NotepadWidget(QWidget):
    def __init__(self, data_manager: NotePadDataManager):
        super().__init__()
        self.data_manager = data_manager

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Initialize Menu
        self.init_menu(layout)

        # Initialize Toolbars
        self.init_toolbar(layout)

        # Initialize Tab Widget
        self.tabs = CustomTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.check_and_close_tab)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        layout.addWidget(self.tabs)

        # Add "탭 추가" Button
        self.add_tab_button = QToolButton(self)
        self.add_tab_button.setIcon(QIcon(":icons/add_tab.png"))
        self.add_tab_button.clicked.connect(lambda: self.new_tab("", "New Tab"))
        self.tabs.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)

        # Load or create initial tab
        self.load_or_create_initial_tab()

    def init_menu(self, layout):
        self.menubar = QMenuBar(self)
        layout.setMenuBar(self.menubar)

        # File Menu
        file_menu = self.menubar.addMenu('File')

        new_action = QAction('New Tab', self)
        new_action.triggered.connect(lambda: self.new_tab("", "New Tab"))
        file_menu.addAction(new_action)

        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_tabs)
        file_menu.addAction(save_action)

    def init_toolbar(self, layout):
        toolbar = QToolBar("Formatting")
        layout.addWidget(toolbar)

        # Bold action
        bold_action = QAction(QIcon(":icons/bold.png"), "Bold", self)
        bold_action.setShortcut(QKeySequence.Bold)
        bold_action.setCheckable(True)
        bold_action.toggled.connect(self.toggle_bold)
        toolbar.addAction(bold_action)

        # Italic action
        italic_action = QAction(QIcon(":icons/italic.png"), "Italic", self)
        italic_action.setShortcut(QKeySequence.Italic)
        italic_action.setCheckable(True)
        italic_action.toggled.connect(self.toggle_italic)
        toolbar.addAction(italic_action)

        # Underline action
        underline_action = QAction(QIcon(":icons/underline.png"), "Underline", self)
        underline_action.setShortcut(QKeySequence.Underline)
        underline_action.setCheckable(True)
        underline_action.toggled.connect(self.toggle_underline)
        toolbar.addAction(underline_action)

        # Font combo box
        self.font_combobox = QFontComboBox(self)
        self.font_combobox.setCurrentFont(QFont("맑은 고딕"))
        self.font_combobox.currentFontChanged.connect(self.change_font)
        toolbar.addWidget(self.font_combobox)

        # Font size combo box
        self.font_size_combobox = QComboBox(self)
        self.font_size_combobox.setEditable(True)
        self.font_size_combobox.addItems([str(i) for i in range(8, 30)])
        self.font_size_combobox.setCurrentText("12")
        self.font_size_combobox.currentIndexChanged[str].connect(self.change_font_size)
        toolbar.addWidget(self.font_size_combobox)

        # Color picker action
        self.color_action = QAction(QIcon(), "Text Color", self)
        self.update_text_color_icon(QColor("black"))
        self.color_action.triggered.connect(self.select_text_color)
        toolbar.addAction(self.color_action)

        # Save action
        save_action = QAction(QIcon(":icons/save.png"), "Save", self)
        save_action.triggered.connect(self.save_tabs)
        toolbar.addAction(save_action)

        # Refresh action
        refresh_action = QAction(QIcon(":icons/refresh.png"), "Refresh", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.refresh_tabs)
        toolbar.addAction(refresh_action)

    def refresh_tabs(self):
        print("Refreshing tabs...")
        try:
            data = self.data_manager.sync_on_startup()
        except Exception as e:
            print(f"Failed to sync with server on refresh: {e}")
            data = self.data_manager.load_from_local() or {"tabs": [], "active_tab_index": 0}

        # 기본 값 설정
        if "tabs" not in data:
            data["tabs"] = []
        if "active_tab_index" not in data:
            data["active_tab_index"] = 0

        self.load_tabs_from_data(data)
        print("Tabs refreshed successfully.")

    def new_tab(self, content="", title="New Tab"):
        editor = CustomTextEdit()

        if content == "":
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            author = "Author: Your Name"  # Replace "Your Name" with the actual author's name
            placeholder_text = f"<p style='color:gray;'>Created on: {current_time}<br>{author}</p><br>"
            editor.setHtml(placeholder_text + content)
        else:
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

    def select_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_text_color(color)
            self.update_text_color_icon(color)

    def set_text_color(self, color):
        editor = self.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            char_format = QTextCharFormat()
            char_format.setForeground(color)
            editor.mergeCurrentCharFormat(char_format)

    def update_text_color_icon(self, color):
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        self.color_action.setIcon(QIcon(pixmap))

    def save_tabs(self):
        print("Saving tabs...")
        tabs_data = []
        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)
            if isinstance(editor, QTextEdit):
                html_content = self.convert_images_to_base64(editor)
                title = self.tabs.tabText(index)
                tabs_data.append({"title": title, "content": html_content})

        # Save the active tab index
        active_tab_index = self.tabs.currentIndex()

        data_to_save = {
            "serial": self.data_manager.serial,
            "active_tab_index": active_tab_index,
            "tabs": tabs_data,
            "version": self.data_manager.get_local_version() + 1
        }

        self.data_manager.save_to_local(data_to_save)
        self.data_manager.save_to_server(data_to_save)

    def load_tabs_from_data(self, data):
        self.tabs.clear()
        tabs_data = data.get("tabs", [])
        for tab in tabs_data:
            self.new_tab(tab.get("content", ""), tab.get("title", "New Tab"))

        # Restore the active tab index
        active_tab_index = data.get("active_tab_index", 0)
        self.tabs.setCurrentIndex(active_tab_index)

    def load_or_create_initial_tab(self):
        try:
            data = self.data_manager.sync_on_startup()
        except Exception as e:
            print(f"Failed to sync with server on startup: {e}")
            data = self.data_manager.load_from_local() or {"tabs": [], "active_tab_index": 0}

        # 기본 값 설정
        if "tabs" not in data:
            data["tabs"] = []
        if "active_tab_index" not in data:
            data["active_tab_index"] = 0

        self.load_tabs_from_data(data)

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

        if not QApplication.clipboard.mimeData().hasImage():
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

class NotepadMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = self.load_settings()
        self.data_manager = NotePadDataManager(
            serial=self.settings.get("serial", "default_serial"),
            local_file=self.settings.get("local_file", "tabs_data.json"),
            server_url=self.settings.get("server_url", "http://192.168.5.118:9338"),
            timeout=1  # 타임아웃 설정
        )
        self.notepad_widget = NotepadWidget(self.data_manager)
        self.setCentralWidget(self.notepad_widget)
        self.setWindowTitle("HTML Notepad")
        self.setGeometry(100, 100, 800, 600)

        # 상태 표시줄 추가
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Add settings action
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.open_settings_dialog)
        self.menuBar().addAction(self.settings_action)

        # Show settings dialog at startup
        self.open_settings_dialog()

        # Show current settings
        self.show_current_settings()

        # 주기적으로 연결 상태 확인
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_server_connection)
        self.timer.start(10000)  # 10초마다 확인

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_settings(self):
        with open("settings.json", "w", encoding='utf-8') as file:
            json.dump(self.settings, file, ensure_ascii=False, indent=4)

    def open_settings_dialog(self):
        from settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.settings, self.data_manager, self)
        if dialog.exec_():
            self.save_settings()
            self.data_manager = NotePadDataManager(
                serial=self.settings.get("serial"),
                local_file=self.settings.get("local_file"),
                server_url=self.settings.get("server_url"),
                timeout=1  # 타임아웃 설정
            )
            self.notepad_widget.data_manager = self.data_manager
            self.notepad_widget.load_or_create_initial_tab()
            self.show_current_settings()

    def show_current_settings(self):
        settings_text = f"Serial: {self.settings.get('serial', '')} | Local File: {self.settings.get('local_file', '')} | Server URL: {self.settings.get('server_url', '')}"
        self.setWindowTitle(f"HTML Notepad - {settings_text}")

    def check_server_connection(self):
        try:
            response = requests.get(f"{self.settings.get('server_url')}/list_serials/", timeout=self.data_manager.timeout)
            response.raise_for_status()
            self.status_bar.showMessage("Connected to server")
        except requests.exceptions.RequestException:
            self.status_bar.showMessage("Failed to connect to server")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Save Changes',
                                     'Do you want to save changes before closing?',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)

        if reply == QMessageBox.Yes:
            self.notepad_widget.save_tabs()
            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = NotepadMainWindow()
    main_window.show()
    sys.exit(app.exec_())