"""Removes the 'update fields on open' flag after Word has updated the fields, so the document opens without a prompt."""
import os
import re
import shutil
import sys
import zipfile

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "EcoServe_AI_Report.docx")
tmp = path + ".tmp"
with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/settings.xml":
            data = re.sub(rb"<w:updateFields[^>]*/>", b"", data)
        zout.writestr(item, data)
shutil.move(tmp, path)
print("finalised", path)
