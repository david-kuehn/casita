import json
import cast_interface
from os import path
from AppKit import NSBundle

app_class = None

# The location of the user_preferences.json file becomes fuzzy based on the app
# context. See: https://github.com/pyinstaller/pyinstaller/issues/5109#issuecomment-683313824
# First, use AppKit to check the (potential) Application Bundle for the JSON file.
# If it's not there, use the os.path approach.
# In this way, preferences will be loaded whether running from source or from binary.
filepath = NSBundle.mainBundle().pathForResource_ofType_("user_preferences", "json")
if filepath == None:
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "user_preferences.json"))

def init_app_class(app_class_ref):
    global app_class
    app_class = app_class_ref

def read_prefs():
    global USER_PREFS

    prefs_file = open(filepath)
    USER_PREFS = json.loads(prefs_file.read())
    prefs_file.close()

    if USER_PREFS["icon"] == "colored":
        set_icon_colored(None)
    elif USER_PREFS["icon"] == "mono":
        set_icon_mono(None)

    return USER_PREFS

def set_icon_colored(sender):
    app_class.template = None

    app_class.app.title = "🏡"
    app_class.app.icon = None

    USER_PREFS["icon"] = "colored"
    wrt_prefs = open("user_preferences.json", "w")
    wrt_prefs.write(json.dumps(USER_PREFS))
    wrt_prefs.close()

def set_icon_mono(sender):
    app_class.app.template = True

    app_class.app.icon = "img/mono-house-blk.png"
    app_class.app.title = None

    USER_PREFS["icon"] = "mono"
    wrt_prefs = open("user_preferences.json", "w")
    wrt_prefs.write(json.dumps(USER_PREFS))
    wrt_prefs.close()

def save_favorite_volume(sender):
    USER_PREFS["volume"] = cast_interface.current_volume_level
    wrt_prefs = open("user_preferences.json", "w")
    wrt_prefs.write(json.dumps(USER_PREFS))
    wrt_prefs.close()

def set_to_favorite_volume(sender):
    cast_interface.set_volume(USER_PREFS["volume"] * 100)
