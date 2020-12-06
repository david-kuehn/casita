import sys
import time
import pychromecast

current_media_status = ""
current_media_status_formatted = ""
current_volume_level = 0.0

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
    # Pychromecast only accepts values from 0-1 for volume, so we have to convert it
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
        global current_media_status_formatted
        current_media_status = status

        new_status_formatted = status.title + " · " + status.artist

        # Only print new status if it's actually a new status
        if new_status_formatted != current_media_status_formatted:
            print(status.title + " · " + status.artist)
            current_media_status_formatted = new_status_formatted
            app_class.update_song_title(current_media_status_formatted)

        if status.player_is_paused == True:
            app_class.update_pauseplay_btn("Play")
        else:
            app_class.update_pauseplay_btn("Pause")

def start_listening(parent_to_update, device_name):

    global app_class
    app_class = parent_to_update

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
            break

    app_class.update_cast_devices(chromecast_names)

    # Start socket client's worker thread and wait for initial status update
    chromecast.wait()

    # Regiester a MediaListener object as a listener for general cast status
    global listenerCast
    listenerCast = StatusListener(chromecast.name, chromecast)
    chromecast.register_status_listener(listenerCast)
    
    # Register a StatusMediaListener object as a media status listener
    global listenerMedia
    listenerMedia = StatusMediaListener(chromecast.name, chromecast)
    chromecast.media_controller.register_status_listener(listenerMedia)

    # Shut down discovery
    pychromecast.discovery.stop_discovery(browser)

def stop_listening():
    global chromecast, listenerCast, listenerMedia
    del listenerCast, listenerMedia
    chromecast.disconnect(blocking=True)
    print("Disconnected")