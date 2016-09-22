# Generate Proper FFMPEG filter arguments
class NoSuchPresetFilter(Exception): pass


preset_filters = {
	'black-and-white': 'hue=s=0',
	'vflip': 'vflip',
	'hflip': 'hflip',
	'fifo': 'fifo',
	'frame-align': 'setpts=PTS-STARTPTS',
	'overlay': 'overlay',
	'setpts': 'setpts',
}


def get_preset_filter(name):
	try:
		return preset_filters[name]
	except KeyError:
		raise NoSuchPresetFilter('%s is not a proper preset filter name' % name)


def make_filter(name,*args,**kwargs):
	''' Make a filter usable. Final string has three forms.
	filter
	filter=value:value:value
	filter=key=value:key=value:key=value
	filter=value:value:key=value:key=value
	'''
	if not args and not kwargs:
		return name
	else:
		prefix = name + '='
		values = ':'.join(args)
		kw = [('%s=%s' % (each,kwargs[each])) for each in kwargs]
		kwvalues = ':'.join(kw)

		if args and kwargs:
			return prefix + values + ':' + kwvalues
		elif not args:
			return prefix + kwvalues
		else:
			return prefix + values
