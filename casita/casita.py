import pychromecast
import rumps
import threading
import time
import cast_interface

# Class that handles menubar app itself
class CasitaApp:
    def __init__(self):
        self.app = rumps.App("Casita", "🏡")
        self.track_title_item = rumps.MenuItem(title="No Song Playing")
        self.track_album_artist_item = rumps.MenuItem(title="")
        self.separator = None
        self.pauseplay_btn = rumps.MenuItem(title="Pause", callback=self.pause_play)
        self.skip_btn = rumps.MenuItem(title="Skip", callback=self.skip)
        self.rewind_btn = rumps.MenuItem(title="Rewind", callback=self.rewind)
        self.volume_slider = rumps.SliderMenuItem(value=0, min_value=0, max_value=100, dimensions=(150, 30), callback=self.change_volume)
        self.cast_devices_parent = rumps.MenuItem(title="Cast Devices")
        self.app.menu = [self.track_title_item, self.track_album_artist_item, self.separator, self.volume_slider, self.pauseplay_btn, self.skip_btn, self.rewind_btn, self.separator, self.cast_devices_parent]
        self.start_thread()

    def run(self):
        self.app.run()

    def start_thread(self):
        CastInterfaceThread(parent=self, device_name="Kitchen display")

    def update_track_details(self, new_details):
        # new_details is of type MediaStatus

        if new_details == None:
            self.track_title_item.title = "No Song Playing"
            self.track_album_artist_item.title = ""
        else:
            self.track_title_item.title = new_details.title
            self.track_album_artist_item.title = new_details.artist + " — " + new_details.album_name

    def update_pauseplay_btn(self, new_status):
        self.pauseplay_btn.title = new_status

    def update_volume_level(self, new_volume):
        self.volume_slider.value = (new_volume*100)

    def update_cast_devices(self, new_cast_devices, new_selected_device):
        if len(self.cast_devices_parent) != 0:
            self.cast_devices_parent.clear()

        for device in new_cast_devices:
            device_to_add = rumps.MenuItem(title=device, callback=self.change_selected_cast_device)
            if device == new_selected_device:
                device_to_add.state = 1
            
            self.cast_devices_parent.add(device_to_add)

    def change_selected_cast_device(self, new_device):
        cast_interface.stop_listening()
        cast_interface.start_listening(self, new_device.title)

    def pause_play(self, sender):
        cast_interface.toggle_pause_play()

    def skip(self, sender):
        cast_interface.skip_track()

    def rewind(self, sender):
        cast_interface.previous_track()

    def change_volume(self, sender):
        cast_interface.set_volume(sender.value)

# Class that defines the thread that interacts with the Chromecast
class CastInterfaceThread(threading.Thread):
    def __init__(self, parent, device_name):
        super(CastInterfaceThread, self).__init__()
        self.daemon = True
        self.parent = parent
        self.device_name = device_name
        self.start()

    def run(self):
        cast_interface.start_listening(self.parent, self.device_name)

# Execution loop
if __name__ == "__main__":
    app = CasitaApp()
    app.run()