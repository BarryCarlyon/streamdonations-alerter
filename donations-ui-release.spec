# -*- mode: python -*-
a = Analysis(['donations-ui.py'],
             pathex=['C:\\Users\\Teak\\Documents\\GitHub\\streamdonations-alerter'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

a.datas += [('logo.png', os.path.join(os.path.abspath('.'), 'logo.png'), 'DATA'),
			('cacert.pem', os.path.join(os.path.abspath('.'), 'cacert.pem'), 'DATA'),
			('icon.ico', os.path.join(os.path.abspath('.'), 'icon.ico'), 'DATA')] # relative path, direct path, type

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Donation Tracker.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon='icon.ico' )
