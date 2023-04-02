from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import os
import json
from Utils import util


class LevelRenderer(QWidget):
    TILE_SIZE = 32
    def __init__(self, level, tiles, table):
        super().__init__()
        self._currentLevel = level
        self._tiles = tiles
        self._table = table
    def paintEvent(self, event):
        painter = QPainter(self)
        width = self.width()
        height = self.height()
        for y in range(height // LevelRenderer.TILE_SIZE):
            for x in range(width // LevelRenderer.TILE_SIZE):
                content = self._currentLevel.get((x, y))
                if content is None:
                    continue
                for tile_name in content:
                    tile_index = self._table[tile_name]
                    if tile_index is None:
                        continue
                    tile_item = self._tiles.item(tile_index)
                    image = tile_item.data(Qt.ItemDataRole.UserRole + 2)
                    offsetX, offsetY = tile_item.data(Qt.ItemDataRole.UserRole + 3)
                    painter.drawImage(x * LevelRenderer.TILE_SIZE - offsetX, y * LevelRenderer.TILE_SIZE - offsetY, image)

class LevelEditor(LevelRenderer):
    def __init__(self, level, tiles, table, tile_selection_model):
        super(LevelEditor, self).__init__(level, tiles, table)
        self._tile_selection_model = tile_selection_model
        self._tileToPaint = None
        self._isDrawing = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            select_idx = self._tile_selection_model.currentIndex()
            if not select_idx.isValid():
                return
            self._isDrawing = True
            self._tileToPaint = self._tiles.itemFromIndex(select_idx).text()
        else:
            self._isDrawing = True
            self._tileToPaint = None
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        x = event.position().x() // self.TILE_SIZE
        y = event.position().y() // self.TILE_SIZE
        tiles_one_area = self._currentLevel.setdefault((x, y), [])
        if self._tileToPaint is None:
            if tiles_one_area:
                tiles_one_area.pop(-1) # ?
                self.repaint()
            return
        if tiles_one_area and tiles_one_area[-1] == self._tileToPaint:
            return
        tiles_one_area.append(self._tileToPaint)
        self.repaint()

    def mouseReleaseEvent(self, event):
        self._isDrawing = False


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.level = {}
        self.currentFile = None
        tiles = QStandardItemModel()
        table = {}
        for name, tile_path in util.scan_tiles():
            table[name] = tiles.rowCount()
            tile_item = QStandardItem(name)
            tile_item.setIcon(QIcon(os.path.abspath(tile_path)))
            image = QImage(os.path.abspath(tile_path))
            tile_item.setData(tile_path)
            tile_item.setData(image, Qt.ItemDataRole.UserRole + 2)
            offsetX = (image.width() - LevelRenderer.TILE_SIZE) // 2
            offsetY = image.height() - LevelRenderer.TILE_SIZE
            tile_item.setData((offsetX, offsetY), Qt.ItemDataRole.UserRole + 3)
            tiles.appendRow(tile_item)

        self.update_windowTitle()
        main_widget = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_widget)
        tile_list_view = QListView()
        tile_list_view.setModel(tiles)
        main_widget.addWidget(tile_list_view)

        editor = LevelEditor(self.level, tiles, table, tile_list_view.selectionModel())
        main_widget.addWidget(editor)

        # add a menu
        bar = QMenuBar()
        self.setMenuBar(bar)
        file_menu = bar.addMenu('&File')

        save_as_action = file_menu.addAction('Save &as')
        import sys
        if sys.platform == 'win32':
            save_as_action.setShortcut('Ctrl+Shift+S')
        else:
            save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as)

        save_action = file_menu.addAction('&Save')
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(self._save)

        open_action = file_menu.addAction('&Open')
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open)
        self.resize(800, 500)

        self.show()

    def save_as(self):
        result = QFileDialog.getSaveFileName(self, 'Save', '.', 'Level files (*.json)')
        if not result or not result[0]:
            return
        self.currentFile = os.path.basename(result[0])
        self.update_windowTitle()
        self._save()

    def _save(self):
        if self.currentFile is None:
            self.save_as()
        save_data = {}
        for key, value in self.level.items():
            save_data['%d_%d' % key] = value
        with open(self.currentFile, 'w') as fd:
            json.dump(save_data, fd)

    def _open(self):
        result = QFileDialog.getOpenFileNames(self, 'Open', '.', 'Level files (*.json)')[0]
        if not result or not result[0]:
            return
        self.currentFile = os.path.basename(result[0])
        self.update_windowTitle()
        self.level.clear()
        load_data = {}
        with open(self.currentFile, 'r') as fd:
            load_data = json.load(fd)
        for key, value in load_data.items():
            x, y = key.split('_')
            self.level[(int(x), int(y))] = value
        self.repaint()

    def update_windowTitle(self):
        if self.currentFile is None:
            self.setWindowTitle('Untitled | My tile editor')
        else:
            self.setWindowTitle('%s | My tile editor' % self.currentFile)

if __name__ == '__main__':
    app = QApplication()

    window = MainApplication()
    window.show()
    app.exec()