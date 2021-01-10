app_class = None

def init_app_class(app_class_ref):
    global app_class
    app_class = app_class_ref

def set_icon_colored(sender):
    app_class.app.title = "🏡"
    app_class.app.icon = None

def set_icon_mono(sender):
    app_class.app.icon = "img/mono-house-blk.png"
    app_class.app.title = None