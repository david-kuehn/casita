import sys
import time
import pychromecast

DEVICE_NAME = ["Kitchen display"]
current_media_status = ""
current_media_status_formatted = ""

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

def start_listening(parent_to_update):
    global app_class
    app_class = parent_to_update

    global chromecasts, browser
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=DEVICE_NAME)
    if not chromecasts:
        print("No chromecast with name \"" + DEVICE_NAME[0] + "\" found.")
        sys.exit(1)
    global chromecast
    chromecast = chromecasts[0]

    # Start socket client's worker thread and wait for initial status update
    chromecast.wait()
    
    # Register a StatusMediaListener object as a media status listener
    listenerMedia = StatusMediaListener(chromecast.name, chromecast)
    chromecast.media_controller.register_status_listener(listenerMedia)

    while True:
        cmd = input("Listening for Chromecast events...\n\n")
        if cmd == "skip":
            skip_track()
        elif cmd == "restart":
            restart_track()
        elif cmd == "previous":
            previous_track()
        elif cmd == "end":
            break

    # Shut down discovery
    pychromecast.discovery.stop_discovery(browser)