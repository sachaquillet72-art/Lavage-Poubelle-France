import shutil
import os
src = r'c:\Users\sacha\Downloads\Python Poubelle\analyse-villes'
dst = r'c:\Users\sacha\Downloads\Python Poubelle\analyse-villes-backup'
if os.path.exists(dst + '.zip'):
    print('Backup already exists at', dst + '.zip')
else:
    shutil.make_archive(dst, 'zip', src)
    print('Created backup:', dst + '.zip')