# set up a single chain.
# The chain looks like this:
# [pad][pad]... filter, filter, filter [pad][pad]...
# multiple inputs and outputs, they are called pads

class FilterIsEmptyInChain(Exception): pass


def get_single_chain(inputpads, outputpads, filters):
	''' concat string to make a suitable single chain
		inputpads = [str, str, str...]
		ouputpads = [str, str, str...]
		filters = [str, str, str] but cannot be empty
	'''
	if not filters:
		raise FilterIsEmptyInChain("At least have one filter inside filters list")
	else:
		head = ''.join(['[%s]' % each for each in inputpads])
		tail = ''.join(['[%s]' % each for each in outputpads])
		middle = ','.join(filters)
		return head + middle + tail


def generate_fifo_chain(inputpad, outputpad):
	''' A quick method to generate a fifo chain '''
	return get_single_chain([inputpad],[outputpad],['fifo'])


def generate_overlay_chains(inputpads, outputpad):
	''' A quick method to generate a list of sequencial chians
		simply overlay each other and then have an end point of outputpad
	'''
	temp_prefix = 'overlaypad'
	length = len(inputpads)
	return_list = []
	below_layer = inputpads[0]
	for i in range(length):
		if i+1 == length-1:
			return_list.append(get_single_chain([below_layer,inputpads[i+1]],[temp_prefix+str(i)],['overlay']))
			break
		else:
			return_list.append(get_single_chain([below_layer,inputpads[i+1]],[temp_prefix+str(i)],['overlay']))
			below_layer = temp_prefix+str(i)

	return_list.append(get_single_chain([temp_prefix+str(length-2)],[outputpad],['fifo']))
	return return_list
