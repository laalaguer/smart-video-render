# Bake a Cake into an acutal Movie Clip mp4
# cake = ['layer','layer','layer'] --> the left side is the bottom, the right side is the upper
# layer = {
#   'uid':'resource file name',
#   'start': 'start frame',
#   'end': 'end frame',
#   'filters': [
#       {'name':'filter-name', 'values':[value1, value2,...], 'kwvalues':{dict}},
#       {dict},
#       {dict},
#   ]
# }
# We can produce a filtergraph, and a command line.

import chain
import effect


def filter_adapter(filterobj):
    ''' convert a filter dict object in a cake layer into a ffmpeg filter str '''
    return effect.make_filter(filterobj['name'], *filterobj['values'], **filterobj['kwvalues'])


def trim_filter_adapter(layerobj):
    ''' convert a layer of cake time requirements in to a ffmpeg filter str '''
    return effect.make_filter(effect.preset_filters['setpts'], *['PTS-STARTPTS'], **{'start_frame': layerobj['start'], 'end_frame': layerobj['end']})


def generate_filtergraph(cake, outputpad):
    ''' from a cake obj, generate a list, each list item is a filter chain, its called filtergraph.
    The return is the list. You can further join the list to form a filter graph string
    '''
    temp_prefix = 'processpad'
    middle_chains = []
    # render each clip with its own effects
    for idx, each in enumerate(cake):
        temp_chain = ''
        temp_str_filters = []
        temp_str_filters.append(trim_filter_adapter(each))
        temp_str_filters.extend([filter_adapter(every)
                                 for every in each['filters']])
        temp_chain = chain.get_single_chain(
            [str(idx)], [temp_prefix + str(idx)], temp_str_filters)
        middle_chains.append(temp_chain)

    temp_pads = [temp_prefix + str(idx) for idx, each in enumerate(cake)]
    # append a overlay list to it
    middle_chains.extend(chain.generate_overlay_chains(temp_pads, outputpad))
    return middle_chains


def get_input_files(cake):
    ''' helper function: get input files from cake
    return real file names on the hard disk (linux style)
    '''
    return [each['uid'] for each in cake]


def generate_full_command_line(cake, result_file_name):
    ''' generate a full command line to ensure a render process'''
    program = 'ffmpeg'
    input_files = ['-i %s' % (each) for each in get_input_files(cake)]
    input_files_str = ' '.join(input_files)
    method = '-filter_complex'
    filtergraph_str = '"%s"' % ';'.join(generate_filtergraph(cake, 'out'))
    sufix = '-map "[out]" %s' % result_file_name

    temp_bucket = [program, input_files_str, method, filtergraph_str, sufix]
    return ' '.join(temp_bucket)
