# -*- mode: python -*-
a = Analysis(['EliteOCR.py'],
             pathex=['C:\\Users\\NoOne\\Desktop\\ED\\EliteOCR'],
             hiddenimports=[],
             hookspath=None,
			 #excludes=['PyQt4'],
             runtime_hooks=['rthook_pyqt4.py'])
 
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
			 
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='EliteOCR.exe',
          icon='icon.ico',
          debug=False,#True,
          strip=None,
          upx=True,
          console=False )

