import pychromecast
import rumps
import threading
import time
import cast_interface

# Class that handles menubar app itself
class CasitaApp:
    def __init__(self):
        self.app = rumps.App("Casita", "🏡")
        self.song_title = rumps.MenuItem(title="No Song Playing")
        self.separator = None
        self.pauseplay_btn = rumps.MenuItem(title="Pause", callback=self.pause_play)
        self.skip_btn = rumps.MenuItem(title="Skip", callback=self.skip)
        self.rewind_btn = rumps.MenuItem(title="Rewind", callback=self.rewind)
        self.app.menu = [self.song_title, self.separator, self.pauseplay_btn, self.skip_btn, self.rewind_btn]
        self.start_thread()

    def run(self):
        self.app.run()

    def start_thread(self):
        CastInterfaceThread(parent=self)

    def update_song_title(self, new_title):
        self.song_title.title = new_title

    def update_pauseplay_btn(self, new_status):
        self.pauseplay_btn.title = new_status

    def pause_play(self, sender):
        cast_interface.toggle_pause_play()

    def skip(self, sender):
        cast_interface.skip_track()

    def rewind(self, sender):
        cast_interface.previous_track()

# Class that defines the thread that interacts with the Chromecast
class CastInterfaceThread(threading.Thread):
    def __init__(self, parent=None):
        super(CastInterfaceThread, self).__init__()
        self.daemon = True
        self.parent = parent
        self.start()

    def run(self):
        cast_interface.start_listening(self.parent)

# Execution loop
if __name__ == "__main__":
    app = CasitaApp()
    app.run()