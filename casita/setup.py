from setuptools import setup

APP = ['casita.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': '../house-icon.icns',
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    name='Casita',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'], install_requires=['rumps']
)