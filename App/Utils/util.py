import os


def scan_tiles():
    for filename in os.listdir('Tiles'):
        name, extension = os.path.splitext(filename)
        if extension != '.png':
            continue
        tile_path = os.path.join('Tiles', filename)
        yield name, tile_path

