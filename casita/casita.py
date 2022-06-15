import rumps
import threading
import cast_interface
import prefs
import sys
import time

# Class that handles menubar app itself
class CasitaApp:
    def __init__(self):
        global USER_PREFS

        self.app = rumps.App("Casita", "🏡")

        prefs.init_app_class(self)

        # Reusable, generic items
        self.quit_btn = rumps.MenuItem(title="Quit", callback=rumps.quit_application)
        self.separator = None

        # Preference items
        self.prefs_parent = rumps.MenuItem(title="Preferences")

        self.prefs_icon_parent = rumps.MenuItem(title="Icon")
        self.prefs_icon_items = [rumps.MenuItem(title="Colored Icon", callback=prefs.set_icon_colored), rumps.MenuItem(title="Monochrome Icon", callback=prefs.set_icon_mono)]

        self.prefs_volume_parent = rumps.MenuItem(title="Volume")
        self.prefs_volume_items = [rumps.MenuItem(title="Set to Favorite Volume", callback=prefs.set_to_favorite_volume), None, rumps.MenuItem(title="Save Current Volume as Favorite", callback=prefs.save_favorite_volume)]

        self.prefs_about_parent = rumps.MenuItem(title="About")
        self.prefs_about_items = [rumps.MenuItem(title="Casita 🏡 | v0.1.5.1"), None, rumps.MenuItem(title="by David Kuehn | Chicago")]
        
        # Initialize prefs
        self.prefs_parent.add(self.prefs_icon_parent)
        self.prefs_parent.add(self.prefs_volume_parent)
        self.prefs_parent.add(self.separator)
        self.prefs_parent.add(self.prefs_about_parent)
        for item in self.prefs_icon_items:
            self.prefs_icon_parent.add(item)
        for item in self.prefs_volume_items:
            self.prefs_volume_parent.add(item)
        for item in self.prefs_about_items:
            self.prefs_about_parent.add(item)

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

        # Initialize preferences
        USER_PREFS = prefs.read_prefs()

        # If there is a default device assigned in the user settings, show the 'connecting' menu. Otherwise, show the 'not connected' menu
        if USER_PREFS["default_device"] != "":
            self.update_menu(self.connecting_menu_items, add_quit=False)
        else:
            self.update_menu(self.not_connected_menu_items, add_quit=False)

        # After initializing the menu UI, start the backend's thread
        self.start_thread(USER_PREFS["default_device"])

    def run(self):
        self.app.run()

    # Start new CastInterfaceThread
    def start_thread(self, device):
        CastInterfaceThread(parent=self, device_name=device)

    # Utility method - repopulates menu with items from new_menu_items
    def update_menu(self, new_menu_items, add_quit = True):
        # Clear the old items out of the menu
        self.app.menu.clear()

        # If there is a device connected, enable the volume preferences. Otherwise, disable them
        if cast_interface.is_connected == True:
            if len(self.prefs_volume_parent) == 1:
                self.prefs_volume_parent.clear()
                for item in self.prefs_volume_items:
                    self.prefs_volume_parent.add(item)
        else:
            self.prefs_volume_parent.clear()
            self.prefs_volume_parent.add(rumps.MenuItem(title="Connect device to configure volume settings."))

        found_quit = False
        found_prefs = False

        # Check for quit and preferences buttons in menu
        for item in new_menu_items:
            if item != None and isinstance(item, rumps.SliderMenuItem) == False:
                if item.title == "Quit":
                    found_quit = True
                elif item.title == "Preferences":
                    found_prefs = True

        # If the preferences don't already exist, add them
        if found_prefs == False:
            new_menu_items.append(self.separator)
            new_menu_items.append(self.prefs_parent)

        # If the quit button doesn't already exist, add it
        if found_quit == False and add_quit == True:
            new_menu_items.append(self.quit_btn)

        self.app.menu = new_menu_items

    # Update track title + album/artist menu items
    def update_track_details(self, new_details):
        # new_details is of type MediaStatus
        if new_details == None:
            self.update_menu(self.not_connected_menu_items)
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
            if item == "Cast Devices" and cast_interface.is_connected == True:
                cast_devices_is_in_menu = True
                break
        
        # If the Cast Devices button isn't already in the menu, add it
        if cast_devices_is_in_menu == False:
            # Insert after the first separator
            for item in self.app.menu:
                if "SeparatorMenuItem" in item:
                    self.app.menu.insert_after(item, self.cast_devices_parent)
                    break
            self.app.menu.insert_after("Cast Devices", self.separator)

        # Alphabetize list of devices
        new_cast_devices.sort()

        # If the list isn't already empty, clear it
        if len(self.cast_devices_parent) != 0:
            self.cast_devices_parent.clear()

        # If the list of new devices isn't empty
        if len(new_cast_devices) != 0:
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
            self.cast_devices_parent.add(None)
        else:
            self.cast_devices_parent.add(rumps.MenuItem(title="No Devices Found"))
            self.cast_devices_parent.add(None)
        self.cast_devices_parent.add(rumps.MenuItem(title="Scan Again", callback=self.scan_again))
            
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

    # Restart discovery process
    def scan_again(self, sender):
        print("Restarting scan...")
        cast_interface.discover_devices(app_class_reference=self)

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
# If there are arguments passed
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            print("Debug mode enabled")
            rumps.debug_mode(True)

    app = CasitaApp()
    app.run()
