import sys
import time
import pychromecast

current_media_status = None
current_track_title = ""
current_volume_level = 0.0
previous_connection_status = ""

def toggle_pause_play():
    if current_media_status.player_is_paused == True:
        chromecast.media_controller.play()
    else:
        chromecast.media_controller.pause()

def skip_track():
    chromecast.media_controller.queue_next()

def previous_track():
    chromecast.media_controller.queue_prev()

def restart_track():
    chromecast.media_controller.seek(0)

def set_volume(new_volume):
    # Pychromecast only accepts values from 0-1 for volume, so it has to be converted
    volume_to_set = new_volume / 100
    chromecast.set_volume(volume_to_set)

class StatusListener:
    def __init__(self, name, cast):
        self.name = name
        self.cast = cast

    def new_cast_status(self, status):
        global current_volume_level
        new_volume_level = status.volume_level

        if new_volume_level != current_volume_level:
            current_volume_level = new_volume_level
            app_class.update_volume_level(new_volume_level)

class StatusMediaListener:
    def __init__(self, name, cast):
        self.name = name
        self.cast = cast

    # status is of type MediaStatus - https://bit.ly/mediastatus
    def new_media_status(self, status):
        global current_media_status
        global current_track_title

        def send_media_update():
            global current_track_title

            print(status.title + " · " + status.artist)
            app_class.update_track_details(status)
            current_track_title = status.title

        if type(status.title) == str:
            if current_media_status == None:
                send_media_update()
            else:
                if current_track_title != status.title:
                    send_media_update()

        if status.player_is_paused == True:
            app_class.update_pauseplay_btn("Play")
        else:
            app_class.update_pauseplay_btn("Pause")

        current_media_status = status

class ConnectionListener:
    def __init__(self):
        pass

    def new_connection_status(self, connection_status):
        global previous_connection_status

        name_for_reconnection = chromecast.name

        # Identify whether or not the 'DISCONNECTED' message is preceded by a 'FAILED_RESOLVE'
        # If it is, then attempt to reconnect. If it isn't, it's probably an intended disconnection
        if previous_connection_status == "FAILED_RESOLVE" and connection_status.status == "DISCONNECTED":
            start_listening(parent_to_update=app_class, device_name=name_for_reconnection, is_reconnection=True)
        
        previous_connection_status = connection_status.status

def start_listening(parent_to_update, device_name, is_reconnection):
    global app_class
    app_class = parent_to_update

    # Tell the app class that we're starting the connection process
    app_class.set_connecting_status(device_name=device_name, is_connecting=True, is_reconnection=is_reconnection)

    global chromecasts, browser
    chromecasts, browser = pychromecast.get_chromecasts()
    if not chromecasts:
        print("No chromecasts found.")
        sys.exit(1)

    chromecast_names = []
    for cast in chromecasts:
        chromecast_names.append(cast.name)

        if cast.name == device_name:
            global chromecast
            chromecast = cast

    # Start socket client's worker thread and wait for initial status update
    chromecast.wait()

    print("Connected to " + chromecast.name)

    app_class.update_cast_devices(chromecast_names, chromecast.name)

    # Register a MediaListener object as a listener for general cast status
    global listenerCast
    listenerCast = StatusListener(chromecast.name, chromecast)
    chromecast.register_status_listener(listenerCast)
    
    # Register a StatusMediaListener object as a media status listener
    global listenerMedia
    listenerMedia = StatusMediaListener(chromecast.name, chromecast)
    chromecast.media_controller.register_status_listener(listenerMedia)

    global listenerConnection
    listenerConnection = ConnectionListener()
    chromecast.register_connection_listener(listenerConnection)

    # Shut down discovery
    pychromecast.discovery.stop_discovery(browser)

    chromecast.socket_client.tries = 1

    # Tell the app class that we're done connecting
    app_class.set_connecting_status(device_name=device_name, is_connecting=False, is_reconnection=is_reconnection)

def stop_listening():
    global chromecast, listenerCast, listenerMedia
    del listenerCast, listenerMedia
    chromecast.disconnect(blocking=True)
    reset_app_class_details()
    print("Disconnected")

def reset_app_class_details():
    global current_media_status
    current_media_status = None
    app_class.update_track_details(None)
    app_class.update_volume_level(0)