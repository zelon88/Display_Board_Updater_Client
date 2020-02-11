# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['build\\Display_Board_Updater_Client.py'],
             pathex=['C:\\Users\\JGrimes\\Desktop\\Useful Stuff\\Software\\Scripts\\Python Scripts\\DisplayBoardUpdater\\Client'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Display_Board_Updater_Client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , version='build\\FileInfo.txt', icon='build\\Icon.ico')
