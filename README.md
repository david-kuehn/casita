# Casita 🏡

<p align="center">
  <img src="https://raw.githubusercontent.com/david-kuehn/casita/master/readme_img.png" width=40%>
</p>

## About
Casita is a macOS app that's used to control media playing on Google Home, Chromecast, and other Cast-enabled devices. The app runs solely in the menubar, so it's always just a click away.

### Benefits
* Lightweight footprint
  - App size is ~20MB
  - Uses ~30MB of RAM
  - Uses virtually no CPU resources
* Works with nearly all Cast-enabled devices—even those not made by Google
* No configuration needed, just start the app and control your media

## Running Casita ![build py2app](https://github.com/david-kuehn/casita/workflows/py2app/badge.svg)
1. Install all the dependencies from [requirements.txt](./requirements.txt) using `pip install -r requirements.txt`
1. Ensure that the build setup is configured correctly in [setup.py](./setup.py). The cloned version should build on your machine, but if it doesn't, changes can be made there.
1. In the project's root directory, run `python3 setup.py py2app`. This command builds a Mac app of the project using [py2app](https://github.com/ronaldoussoren/py2app).
1. The newly-generated application can be found in the `dist` directory.
