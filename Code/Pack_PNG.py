import os
import sys

from PySide2.QtCore import QByteArray, QBuffer
from PySide2.QtGui import QImage


class GlobalVariables:
    app_compiled = None
    app_dir = None
    app_exe = None
    gip_path = None


def new_icon_obj(name="",
                 path=""):
    return {
        "name": name,
        "path": path,
    }


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        GlobalVariables.app_compiled = True
        GlobalVariables.app_dir = os.path.dirname(sys.executable)
        GlobalVariables.app_exe = os.path.basename(sys.executable)
    else:
        GlobalVariables.app_compiled = False
        GlobalVariables.app_dir = os.path.dirname(os.path.abspath(__file__))
        GlobalVariables.app_exe = os.path.basename(__file__)

    png_source_dir = os.path.join(GlobalVariables.app_dir, "PNG")
    png_source_files = os.listdir(png_source_dir)
    GlobalVariables.gip_path = os.path.join(GlobalVariables.app_dir, "GML_Qt", "Icon", "__init__.py")

    gip_source_code = """
from PySide2.QtCore import QByteArray
from PySide2.QtGui import QPixmap, QIcon

Icons = %s


def get_pixmap(icon_name):
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray.fromBase64(Icons[icon_name]))

    return pixmap


def get_icon(icon_name):
    return QIcon(get_pixmap(icon_name))
"""

    icons = {}
    for file in png_source_files:
        if file.endswith(".png"):
            name = file.split(".png")[0]
            path = os.path.join(png_source_dir, file)
            icons[name] = new_icon_obj(name=name, path=path)

    output_dict = {}

    for icon_key in icons.keys():
        image = QImage(icons[icon_key]["path"])
        ba = QByteArray()
        buff = QBuffer(ba)
        image.save(buff, "PNG")
        output_dict[icon_key] = ba.toBase64().data()

    try:
        os.makedirs(os.path.dirname(GlobalVariables.gip_path))
    except:
        pass

    with open(GlobalVariables.gip_path, "w") as f:
        final_python_code = gip_source_code % (str(output_dict),)
        f.write(final_python_code)

    print("IconPack Generated -> " + GlobalVariables.gip_path)
