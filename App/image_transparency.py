from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from App.Utils import util

if __name__ == '__main__':
    app = QApplication()
    for name, tile_path in util.scan_tiles():
        image = QImage(tile_path).convertToFormat(QImage.Format.Format_ARGB32)
        binary = image.bits()
        isChanged = False
        for y in range(image.height()):
            for x in range(image.width()):
                pixel_id = (y * image.height() + x) * 4
                blue = binary[pixel_id]
                green = binary[pixel_id + 1]
                red = binary[pixel_id + 2]
                if (blue, green, red) == (255, 0, 255) and binary[pixel_id + 3]:
                    binary[pixel_id + 3] = 0
                    isChanged = True
        if isChanged:
            image.save(tile_path)
            print("Changed %s" % name)