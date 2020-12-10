<p align="center">
  <img src="https://raw.githubusercontent.com/david-kuehn/casita/master/house-icon.png" width=20% style="margin-right: 32px">
</p>

<h1 align="center">Casita</h1>

<p align="center">
  <img src="https://github.com/david-kuehn/casita/workflows/py2app/badge.svg">
</p>

<p align="center">
  A macOS menubar app used to control media playing on Google Home, Chromecast, and other Cast-enabled devices.
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/david-kuehn/casita/master/readme_img.png" width="70%">
</p>

### Details
* Lightweight footprint
  - App size is ~20MB
  - Energy impact always hovers around 0.0, according to Activity Monitor
  - Uses ~30MB of RAM
  - Uses virtually no CPU resources
* Works with nearly all Cast-enabled devices—even those not made by Google
* No configuration needed, just start the app and control your media

### Technologies
* Python 3.x
* [pychromecast](https://github.com/home-assistant-libs/pychromecast)
* [rumps](https://github.com/jaredks/rumps)

## Running Casita
### Building the macOS App
1. Install all the dependencies from [requirements.txt](./requirements.txt).
   - `pip install -r requirements.txt`
1. In the project's root directory, build the app using [py2app](https://github.com/ronaldoussoren/py2app).
   - `python3 setup.py py2app`
1. The newly-generated application can be found in the `dist` directory.
   - Run the generated macOS app!

### Running Uncompiled from Terminal
1. Run the command `python3 casita/casita.py`.
   - This can be run with the `--debug` flag to enable [rumps debug mode](https://github.com/jaredks/rumps/blob/5a868f4fae5e51ccbc95d426e55d689515834b6e/rumps/rumps.py#L33-L42), which gives some extra output corresponding to UI interaction.
1. To quit, use the 'Quit' button in the app's UI, or close the terminal instance.
