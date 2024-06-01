from PyQt5.QtCore import QUrl, QBuffer
from PyQt5.QtWidgets import QFileDialog, QTextEdit
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextImageFormat
import base64
import re

class FileManager:
    def __init__(self, parent):
        self.parent = parent

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.parent, "Open File", "", "HTML Files (*.html);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as file:
                html_content = file.read()
                self.parent.new_tab(html_content, file_name.split('/')[-1])

    def save_tabs(self):
        print("Saving tabs...")
        tabs_data = []
        for index in range(self.parent.tabs.count()):
            editor = self.parent.tabs.widget(index)
            if isinstance(editor, QTextEdit):
                html_content = self.convert_images_to_base64(editor)
                title = self.parent.tabs.tabText(index)
                tabs_data.append({"title": title, "content": html_content})

        # Save the active tab index
        active_tab_index = self.parent.tabs.currentIndex()

        data_to_save = {
            "serial": self.parent.data_manager.serial,
            "active_tab_index": active_tab_index,
            "tabs": tabs_data,
            "version": self.parent.data_manager.get_local_version() + 1
        }

        self.parent.data_manager.save_to_local(data_to_save)
        self.parent.data_manager.save_to_server(data_to_save)

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
