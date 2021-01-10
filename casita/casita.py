import pychromecast
import rumps
import threading
import time
import cast_interface
import sys
import json
from os import path

# Class that handles menubar app itself
class CasitaApp:
    def __init__(self):
        global USER_SETTINGS

        self.app = rumps.App("Casita", "🏡")

        # Reusable, generic items
        self.quit_btn = rumps.MenuItem(title="Quit", callback=rumps.quit_application)
        self.separator = None

        # Items to display when no device is connected
        self.no_device_item = rumps.MenuItem(title="No Device Connected")
        self.cast_devices_parent = rumps.MenuItem(title="Cast Devices")
        self.not_connected_menu_items = [self.no_device_item, self.separator]

        # Items to display in menu while connecting to Cast device
        self.connecting_item = rumps.MenuItem(title="Connecting...")
        self.connecting_menu_items = [self.connecting_item, self.quit_btn]

        # Items to display in menu while media is playing on a Cast device
        self.track_title_item = rumps.MenuItem(title="No Song Playing")
        self.track_album_artist_item = rumps.MenuItem(title="")
        self.pauseplay_btn = rumps.MenuItem(title="Pause", callback=self.pause_play)
        self.skip_btn = rumps.MenuItem(title="Skip", callback=self.skip)
        self.rewind_btn = rumps.MenuItem(title="Rewind", callback=self.rewind)
        self.volume_slider = rumps.SliderMenuItem(value=0, min_value=0, max_value=100, dimensions=(150, 30), callback=self.change_volume)
        self.playing_menu_items = [self.track_title_item, self.track_album_artist_item, self.separator, self.volume_slider, self.pauseplay_btn, self.skip_btn, self.rewind_btn, self.separator, self.cast_devices_parent]
        
        # Items to display in menu while connected, but no media is playing
        self.no_song_item = rumps.MenuItem(title="No Song Playing")
        self.idle_menu_items = [self.no_song_item, self.separator, self.volume_slider, self.separator, self.cast_devices_parent]

        # If there is a default device assigned in the user settings, show the 'connecting' menu. Otherwise, show the 'not connected' menu
        if USER_SETTINGS["default_device"] != "":
            # Show the connecting menu items
            self.app.menu = self.connecting_menu_items
        else:
            self.app.menu = self.not_connected_menu_items

        # After initializing the menu UI, start the backend's thread
        self.start_thread(USER_SETTINGS["default_device"])

    def run(self):
        self.app.run()

    # Start new CastInterfaceThread
    def start_thread(self, device):
        CastInterfaceThread(parent=self, device_name=device)

    # Utility method - repopulates menu with items from new_menu_items
    def update_menu(self, new_menu_items):
        # Clear the old items out of the menu
        self.app.menu.clear()

        # If the last menu is not a quit button, add one
        if new_menu_items[-1].title != "Quit":
            new_menu_items.append(self.separator)
            new_menu_items.append(self.quit_btn)

        self.app.menu = new_menu_items

    # Update track title + album/artist menu items
    def update_track_details(self, new_details):
        # new_details is of type MediaStatus
        if new_details == None:
            self.update_menu(self.idle_menu_items)
        else:
            # If the menu is currently showing the controls for when media is playing (there are 7 items in the idle controls)
            if len(self.app.menu) > 9:
                # Just reset the song, artist, and album
                self.track_title_item.title = new_details.title
                self.track_album_artist_item.title = new_details.artist + " — " + new_details.album_name
            else:
                # Clear the menu and add the playing menu items
                self.update_menu(self.playing_menu_items)

                # Then, reset the song, artist, and album
                self.track_title_item.title = new_details.title
                self.track_album_artist_item.title = new_details.artist + " — " + new_details.album_name                       

    # Update menu item to reflect paused/playing status
    def update_pauseplay_btn(self, new_status):
        self.pauseplay_btn.title = new_status

    # Update value of volume slider
    def update_volume_level(self, new_volume):
        self.volume_slider.value = (new_volume*100)

    # Update list of cast devices
    def update_cast_devices(self, new_cast_devices, new_selected_device):
        # Determine if the Cast Devices button is already in the menu
        cast_devices_is_in_menu = False
        for item in self.app.menu:
            if item == "Cast Devices":
                cast_devices_is_in_menu = True
        
        # If the Cast Devices button isn't already in the menu, add it
        if cast_devices_is_in_menu == False:
            self.app.menu.insert_after("SeparatorMenuItem_1", self.cast_devices_parent)
            self.app.menu.insert_after("Cast Devices", self.separator)

        # Alphabetize list of devices
        new_cast_devices.sort()

        # If the list isn't already empty, clear it
        if len(self.cast_devices_parent) != 0:
            self.cast_devices_parent.clear()

        for device in new_cast_devices:
            device_to_add = rumps.MenuItem(title=device, callback=self.change_selected_cast_device)

            # If the currently-iterating device is the newly-selected device
            if device == new_selected_device:
                # Mark it as enabled and insert it into the first position in the menu
                device_to_add.state = 1
                self.cast_devices_parent.insert_before(self.cast_devices_parent[new_cast_devices[0]].title, device_to_add)
                self.cast_devices_parent.insert_after(self.cast_devices_parent[device].title, None)
            else:
                self.cast_devices_parent.add(device_to_add)
            
    # Update the menu items to reflect the current connection status
    def set_connecting_status(self, device_name, is_connecting, is_reconnection, did_succeed):
        # If we're connecting
        if is_connecting == True:
            # If we're reconnecting
            if is_reconnection == True:
                self.connecting_item.title = "Reconnecting to " + device_name + "..."
            else:
                self.connecting_item.title = "Connecting to " + device_name + "..."
            
            # Repopulate the menu with the connecting items
            self.update_menu(self.connecting_menu_items)
        else:
            if did_succeed == True:
                # Populate the menu with the idle items
                self.update_menu(self.idle_menu_items)
            else:
                # Populate the menu with the disconnected items
                self.update_menu(self.not_connected_menu_items)

    #
    # Begin functions that interact with backend
    #

    # Switch the device we're monitoring
    def change_selected_cast_device(self, new_device):
        # If currently connected, disconnect
        if cast_interface.is_connected == True:
            cast_interface.stop_listening()
        cast_interface.start_listening(self, new_device.title, False)

    # Toggle pause/play
    def pause_play(self, sender):
        cast_interface.toggle_pause_play()

    # Skip current track
    def skip(self, sender):
        cast_interface.skip_track()

    # Go back to previous track
    def rewind(self, sender):
        cast_interface.previous_track()

    # Change volume of media
    def change_volume(self, sender):
        cast_interface.set_volume(sender.value)

# Class defining the thread that interacts with the Chromecast
class CastInterfaceThread(threading.Thread):
    def __init__(self, parent, device_name):
        super(CastInterfaceThread, self).__init__()
        self.daemon = True
        self.parent = parent
        self.device_name = device_name
        self.start()

    def run(self):
        # If there is a device passed, tell cast_interface to start listening to that device
        # If not, tell cast_interface to just discover
        if self.device_name != "":
            cast_interface.start_listening(app_class_reference=self.parent, device_name=self.device_name, is_reconnection=False)
        else:
            # Just Discover
            print("No default device. Attempting to start discovery.")
            cast_interface.discover_devices(app_class_reference=self.parent)
        

# Execution loop
if __name__ == "__main__":
    # Get user settings
    global USER_SETTINGS
    settings_file = open("user_settings.json")
    USER_SETTINGS = json.loads(settings_file.read())
    print(USER_SETTINGS)

    # If there are arguments passed
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            print("Debug mode enabled")
            rumps.debug_mode(True)

    app = CasitaApp()
    app.run()
