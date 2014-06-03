streamdonations-alerter
=======================

Real-time alerts for http://streamdonations.net

Only dependancies (before packaging) are WxPython and socketIO_client

Uses PyInstaller for packaging. All non-imported resources (icon and such) must be added to the spec file.

To package, download PyInstaller and run

    pyinstaller donations-ui-release.spec

or

    pyinstaller donations-ui-debug.spec

Debug version does not package into one file and includes a console...

For now the settings.ini file will be created and read from the same dirctory as the script/exe
