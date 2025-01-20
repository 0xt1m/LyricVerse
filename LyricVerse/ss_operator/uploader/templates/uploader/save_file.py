import os

fi = form['filename']
if fi.filename:
	fil = os.path.basename(fi.filename)
	open(fn, 'wb').write(fi.file.read())