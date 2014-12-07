# -*- mode: python -*-
a = Analysis(['EliteOCR.py'],
             pathex=['C:\\Users\\Sebastian\\Desktop\\plugintest'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='EliteOCR.exe',
          icon='icon.ico',
          debug=False,
          strip=None,
          upx=True,
          console=False)
