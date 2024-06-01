from PyQt5.QtWidgets import QTextEdit, QMenu, QAction, QMessageBox
from datetime import datetime

class TabManager:
    def __init__(self, parent):
        self.parent = parent

    def check_and_close_tab(self, index):
        editor = self.parent.tabs.widget(index)
        if isinstance(editor, QTextEdit):
            if editor.toPlainText().strip():
                reply = QMessageBox.question(self.parent, 'Close Tab',
                                             'This tab contains content. Are you sure you want to close it? This action cannot be undone.',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.close_tab(index)
            else:
                self.close_tab(index)

    def close_tab(self, index):
        self.parent.tabs.removeTab(index)
        if self.parent.tabs.count() == 0:
            self.new_tab()

    def show_tab_context_menu(self, position):
        index = self.parent.tabs.tabBar().tabAt(position)
        if index != -1:
            menu = QMenu()

            duplicate_right_action = QAction("Duplicate to the Right", self.parent)
            duplicate_right_action.triggered.connect(lambda: self.duplicate_tab_right(index))
            menu.addAction(duplicate_right_action)

            duplicate_left_action = QAction("Duplicate to the Left", self.parent)
            duplicate_left_action.triggered.connect(lambda: self.duplicate_tab_left(index))
            menu.addAction(duplicate_left_action)

            new_tab_right_action = QAction("New Tab to the Right", self.parent)
            new_tab_right_action.triggered.connect(lambda: self.new_tab_right(index))
            menu.addAction(new_tab_right_action)

            new_tab_left_action = QAction("New Tab to the Left", self.parent)
            new_tab_left_action.triggered.connect(lambda: self.new_tab_left(index))
            menu.addAction(new_tab_left_action)

            close_action = QAction("Close Tab", self.parent)
            close_action.triggered.connect(lambda: self.check_and_close_tab(index))
            menu.addAction(close_action)

            menu.exec_(self.parent.tabs.tabBar().mapToGlobal(position))

    def new_tab(self, content="", title="New Tab"):
        editor = QTextEdit()

        if content == "":
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            author = "Author: Your Name"  # Replace "Your Name" with the actual author's name
            placeholder_text = f"<p style='color:gray;'>Created on: {current_time}<br>{author}</p><br>"
            editor.setHtml(placeholder_text + content)
        else:
            editor.setHtml(content)

        index = self.parent.tabs.addTab(editor, title)
        self.parent.tabs.setCurrentIndex(index)

    def new_tab_right(self, index):
        self.new_tab()
        self.parent.tabs.tabBar().moveTab(self.parent.tabs.count() - 1, index + 1)

    def new_tab_left(self, index):
        self.new_tab()
        self.parent.tabs.tabBar().moveTab(self.parent.tabs.count() - 1, index)

    def generate_duplicate_title(self, title):
        base_title = title.split('_')[0]
        max_suffix = 1
        for i in range(self.parent.tabs.count()):
            tab_title = self.parent.tabs.tabText(i)
            if (tab_title.startswith(base_title) and
                len(tab_title.split('_')) > 1 and
                tab_title.split('_')[-1].isdigit()):
                suffix = int(tab_title.split('_')[-1])
                if suffix >= max_suffix:
                    max_suffix = suffix + 1
        return f"{base_title}_{max_suffix}"

    def duplicate_tab_right(self, index):
        current_editor = self.parent.tabs.widget(index)
        if isinstance(current_editor, QTextEdit):
            html_content = current_editor.toHtml()
            title = self.parent.tabs.tabText(index)
            new_title = self.generate_duplicate_title(title)
            self.new_tab_right(index)
            new_editor = self.parent.tabs.widget(index + 1)
            new_editor.setHtml(html_content)
            self.parent.tabs.setTabText(index + 1, new_title)

    def duplicate_tab_left(self, index):
        current_editor = self.parent.tabs.widget(index)
        if isinstance(current_editor, QTextEdit):
            html_content = current_editor.toHtml()
            title = self.parent.tabs.tabText(index)
            new_title = self.generate_duplicate_title(title)
            self.new_tab_left(index)
            new_editor = self.parent.tabs.widget(index)
            new_editor.setHtml(html_content)
            self.parent.tabs.setTabText(index, new_title)

    def toggle_bold(self, checked):
        editor = self.parent.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            if checked:
                editor.setFontWeight(QFont.Bold)
            else:
                editor.setFontWeight(QFont.Normal)

    def toggle_italic(self, checked):
        editor = self.parent.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            editor.setFontItalic(checked)

    def toggle_underline(self, checked):
        editor = self.parent.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            editor.setFontUnderline(checked)

    def change_font(self, font):
        editor = self.parent.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            editor.setCurrentFont(font)

    def change_font_size(self, size):
        editor = self.parent.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            editor.setFontPointSize(float(size))

    def select_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_text_color(color)
            self.parent.toolbar.update_text_color_icon(color)

    def set_text_color(self, color):
        editor = self.parent.tabs.currentWidget()
        if isinstance(editor, QTextEdit):
            char_format = QTextCharFormat()
            char_format.setForeground(color)
            editor.mergeCurrentCharFormat(char_format)

    def refresh_tabs(self):
        print("Refreshing tabs...")
        try:
            data = self.parent.data_manager.sync_on_startup()
        except Exception as e:
            print(f"Failed to sync with server on refresh: {e}")
            data = self.parent.data_manager.load_from_local() or {"tabs": [], "active_tab_index": 0}

        # 기본 값 설정
        if "tabs" not in data:
            data["tabs"] = []
        if "active_tab_index" not in data:
            data["active_tab_index"] = 0

        self.load_tabs_from_data(data)
        print("Tabs refreshed successfully.")

    def load_tabs_from_data(self, data):
        self.parent.tabs.clear()
        tabs_data = data.get("tabs", [])
        for tab in tabs_data:
            self.new_tab(tab.get("content", ""), tab.get("title", "New Tab"))

        # Restore the active tab index
        active_tab_index = data.get("active_tab_index", 0)
        self.parent.tabs.setCurrentIndex(active_tab_index)

    def load_or_create_initial_tab(self):
        try:
            data = self.parent.data_manager.sync_on_startup()
        except Exception as e:
            print(f"Failed to sync with server on startup: {e}")
            data = self.parent.data_manager.load_from_local() or {"tabs": [], "active_tab_index": 0}

        # 기본 값 설정
        if "tabs" not in data:
            data["tabs"] = []
        if "active_tab_index" not in data:
            data["active_tab_index"] = 0

        self.load_tabs_from_data(data)
