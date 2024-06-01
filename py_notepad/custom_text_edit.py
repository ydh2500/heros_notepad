from datetime import datetime

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QTextImageFormat, QTextDocument
from PyQt5.QtWidgets import QTextEdit


class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def insertFromMimeData(self, source):
        if source.hasImage():
            image = source.imageData()
            self.insert_image(image)
        else:
            super().insertFromMimeData(source)

    def insert_image(self, image):
        cursor = self.textCursor()
        document = self.document()
        image_format = QTextImageFormat()
        image_name = f'image_{datetime.now().strftime("%Y%m%d%H%M%S%f")}.png'
        document.addResource(QTextDocument.ImageResource, QUrl(image_name), image)
        image_format.setName(image_name)
        cursor.insertImage(image_format)
