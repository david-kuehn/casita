import pychromecast

chromecasts, browser = pychromecast.get_chromecasts()
pychromecast.discovery.stop_discovery(browser)

for cast in chromecasts:
	print(cast.name)