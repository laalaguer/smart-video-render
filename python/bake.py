# Target:
# We have: a list, each list item is a clip.
# each clip has a effect on it.
# we output the overlay of the clips.
# we output the command line to deal with the video rendering.

# ['item','item','item'] --> the left side is the bottom, the right side is the upper
# item {
# 	'uid':'resource file name',
# 	'start': 'start time',
# 	'effect': ['filter', 'filter', 'filter']
# }

# what to output?

# a filtergraph to output all the sequence into one output file
# So we need a filtergraph, we also need a command line that we can execute

effect_dict = {
	'blackandwhite': 'hue=s=0',
	'vflip': 'vflip',
	'hflip': 'hflip',
	'fifo': 'fifo',
}

cakes = [
	{'uid':'file-1.mp4', 'start':'0', 'effect':['vflip']},
	{'uid':'file-2.mp4', 'start':'12', 'effect':['hflip','blackandwhite']},
	{'uid':'file-3.mp4', 'start':'20', 'effect':['blackandwhite']},
]

# [0] some filter [processed0]
# [1] some filter [processed1]
# [processed0][processed1] overlay [overlay0]
# [overlay0]fifo[out]

# The final string will be
# [0] some filter [processed0]
# [1] some filter [processed1]
# [2] some filter [processed2]
# [3] some filter [processed3]
# [processed0][processed1] overlay [overlay0]
# [overlay0][processed2] overlay [overlay1]
# [overlay1][processed3] overlay [overlay2]
# [overlay2]fifo[out]

def get_single_chain(inputname, outputname, effectnamelist, effect_dict):
	if not effectnamelist: # len() = 0
		return '[%s]%s[%s]' % (inputname, 'fifo', outputname)
	else:
		effects = [effect_dict[each] for each in effectnamelist]
		effect_chain = ','.join(effects)
		return '[%s]%s[%s]' % (inputname, effect_chain, outputname)

def get_overlay_chain(belowname,overname,outputname):
	return '[%s][%s]overlay[%s]' % (belowname,overname,outputname)

def get_input_files(cakelist):
	return [each['uid'] for each in cakelist]

def generate_overlay_block(padlist):
	temp_prefix = 'overlay'
	length = len(padlist)
	return_list = []
	below_layer = padlist[0]
	for i in range(length):
		if i+1 == length-1:
			return_list.append(get_overlay_chain(below_layer,padlist[i+1],temp_prefix+str(i)))
			break
		else:
			return_list.append(get_overlay_chain(below_layer,padlist[i+1],temp_prefix+str(i)))
			below_layer = temp_prefix+str(i)

	return_list.append(get_single_chain(temp_prefix+str(length-2),'out',['fifo'], effect_dict))
	return return_list

def generate_filtergraph(cakelist):
	temp_prefix = 'processed'
	middle_chains = []
	# render each clip with its own effects
	for idx, each in enumerate(cakelist):
		# TODO --- split the code out
		chain = get_single_chain(str(idx),temp_prefix+str(idx),each['effect'],effect_dict)
		middle_chains.append(chain)

	temp_pads = [temp_prefix+str(idx) for idx, each in enumerate(cakelist)]
	# append a overlay list to it
	middle_chains.extend(generate_overlay_block(temp_pads))
	filter_graph_str = ';'.join(middle_chains)
	return filter_graph_str


def generate_full_command_line(cakelist):
	''' generate a full command line to ensure a render '''
	program = 'ffmpeg'
	input_list = ['-i %s' % (each) for each in get_input_files(cakelist)]
	input_list_str = ' '.join(input_list)
	method = '-filter_complex'
	filtergraph_str = '"%s"' % generate_filtergraph(cakelist)
	sufix = '-map "[out]" result.mp4'

	temp_bucket = [program,input_list_str,method,filtergraph_str,sufix]
	return ' '.join(temp_bucket)

print get_single_chain('in','out',['blackandwhite','vflip'], effect_dict)
print get_overlay_chain('below','upper','out')
print get_input_files(cakes)
print generate_filtergraph(cakes)
print generate_full_command_line(cakes)