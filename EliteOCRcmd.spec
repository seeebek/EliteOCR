# -*- mode: python -*-

block_cipher = None


a = Analysis(['EliteOCRcmd.py'],
             pathex=['C:\\Users\\SEBAST~1\\Desktop\\RFACTO~2'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             cipher=block_cipher)
pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='EliteOCRcmd.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='EliteOCRcmd')
