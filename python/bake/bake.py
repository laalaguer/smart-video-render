# ['item','item','item'] --> the left side is the bottom, the right side is the upper
# item {
# 	'uid':'resource file name',
# 	'trim-start': 'start time',
#	'trim-end': 'end time',
# 	'effect': ['filter', 'filter', 'filter']
# }
# a filtergraph to output all the sequence into one output file
# So we need a filtergraph, we also need a command line that we can execute
cake = [
	{'uid':'file-1.mp4', 'trim-start':'0', 'trim-end': '10',  'effect':['vflip']},
	{'uid':'file-2.mp4', 'trim-start':'12', 'trim-end': '22', 'effect':['hflip','blackandwhite']},
	{'uid':'file-3.mp4', 'trmi-start':'20', 'trim-end': '30', 'effect':['blackandwhite']},
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

def get_single_chain(inputpad, outputpad, effects, effect_dict):
	if not effects: # len() = 0
		return '[%s]%s[%s]' % (inputpad, 'fifo', outputpad)
	else:
		effects = [effect_dict[each] for each in effects]
		effect_chain = ','.join(effects)
		return '[%s]%s[%s]' % (inputpad, effect_chain, outputpad)

def get_overlay_chain(belowname,overname,outputname):
	return '[%s][%s]overlay[%s]' % (belowname,overname,outputname)

def get_input_files(cake):
	return [each['uid'] for each in cake]

def generate_overlay_block(pads):
	temp_prefix = 'overlay'
	length = len(pads)
	return_list = []
	below_layer = pads[0]
	for i in range(length):
		if i+1 == length-1:
			return_list.append(get_overlay_chain(below_layer,pads[i+1],temp_prefix+str(i)))
			break
		else:
			return_list.append(get_overlay_chain(below_layer,pads[i+1],temp_prefix+str(i)))
			below_layer = temp_prefix+str(i)

	return_list.append(get_single_chain(temp_prefix+str(length-2),'out',['fifo'], effect_dict))
	return return_list

def generate_filtergraph(cake):
	temp_prefix = 'processed'
	middle_chains = []
	# render each clip with its own effects
	for idx, each in enumerate(cake):
		# TODO --- split the code out
		chain = get_single_chain(str(idx),temp_prefix+str(idx),each['effect'],effect_dict)
		middle_chains.append(chain)

	temp_pads = [temp_prefix+str(idx) for idx, each in enumerate(cake)]
	# append a overlay list to it
	middle_chains.extend(generate_overlay_block(temp_pads))
	filter_graph_str = ';'.join(middle_chains)
	return filter_graph_str


def generate_full_command_line(cake):
	''' generate a full command line to ensure a render '''
	program = 'ffmpeg'
	input_list = ['-i %s' % (each) for each in get_input_files(cake)]
	input_list_str = ' '.join(input_list)
	method = '-filter_complex'
	filtergraph_str = '"%s"' % generate_filtergraph(cake)
	sufix = '-map "[out]" result.mp4'

	temp_bucket = [program,input_list_str,method,filtergraph_str,sufix]
	return ' '.join(temp_bucket)

print get_single_chain('in','out',['blackandwhite','vflip'], effect_dict)
print get_overlay_chain('below','upper','out')
print get_input_files(cake)
print generate_filtergraph(cake)
print generate_full_command_line(cake)