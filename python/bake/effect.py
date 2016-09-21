# Generate Proper FFMPEG filter arguments
quick_effect = {
	'blackandwhite': 'hue=s=0',
	'vflip': 'vflip',
	'hflip': 'hflip',
	'fifo': 'fifo',
	'frame-align': 'setpts=PTS-STARTPTS',
}

def get_effect(name):
	try:
		return quick_effect[name]
	except KeyError:
		raise NoSuchEffect('%s is not a proper quick filter name' % name)

class NoSuchEffect(Exception): pass