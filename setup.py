from setuptools import setup

VERSION = '0.1.5.2'

APP = ['casita/casita.py']
DATA_FILES = [
    ('', ['casita/user_preferences.json']),
    ('', ['casita/img'])
]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'house-icon.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleShortVersionString': '0.1.5.2',
    },
    'packages': ['rumps', 'zeroconf'],
}

setup(
    app=APP,
    name='Casita',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'], install_requires=['rumps', 'zeroconf']
)
