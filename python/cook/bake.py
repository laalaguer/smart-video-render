# Bake a Cake into an acutal Movie Clip mp4
# cake = {
#     'layers': [layer, layer, layer], -- > the left side is the bottom, the right side is the upper
#     'uid': xxx ---> xxx-rangestart-rangeend --> hash id and range of the cake
# }
#
# layer = {
#   'resource':'resource file name',
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
    return effect.make_filter(
        effect.preset_filters['trim'],
        **{'start_frame': layerobj['start'], 'end_frame': layerobj['end']}
    )


def setpts_filter_adapter(layerobj):
    ''' convert a layer of cake to align again into first frame '''
    return effect.make_filter(effect.preset_filters['setpts'], *['PTS-STARTPTS'])


def generate_filtergraph(cake, outputpad):
    ''' From a cake obj, generate a list,
    each list item is a filter chain, its called filtergraph.
    The return is the list.
    You can further join the list to form a filter graph string
    '''
    temp_prefix = 'processpad'
    middle_chains = []
    # render each clip with its own effects
    for idx, each in enumerate(cake['layers']):
        temp_chain = ''
        temp_str_filters = []
        temp_str_filters.append(trim_filter_adapter(each))
        temp_str_filters.append(setpts_filter_adapter(each))
        temp_str_filters.extend([filter_adapter(every)
                                 for every in each['filters']])
        temp_chain = chain.get_single_chain(
            [str(idx)], [temp_prefix + str(idx)], temp_str_filters)
        middle_chains.append(temp_chain)

    if len(cake['layers']) == 1:
        # print chain.generate_fifo_chain(temp_prefix + str(0), outputpad)
        middle_chains.append(chain.generate_fifo_chain(temp_prefix + str(0), outputpad))
        return middle_chains
    else:
        temp_pads = [temp_prefix + str(idx) for idx, each in enumerate(cake['layers'])]
        # append a overlay list to it
        middle_chains.extend(chain.generate_overlay_chains(temp_pads, outputpad))

    return middle_chains


def get_input_files(cake):
    ''' helper function: get input files from cake
    return real file names on the hard disk (linux style)
    '''
    return [each['resource'] for each in cake['layers']]


def generate_single_render_command_line(cake, result_file_name):
    ''' Generate a full command line to ensure a render process'''
    program = 'ffmpeg'
    input_files = ['-i %s' % (each) for each in get_input_files(cake)]
    input_files_str = ' '.join(input_files)
    method = '-filter_complex'
    filtergraph_str = '"%s"' % ';'.join(generate_filtergraph(cake, 'out'))
    output_format = '-codec:v libx264 -crf 18 -preset slow'
    sufix = '-map "[out]" %s' % result_file_name

    temp_bucket = [program, input_files_str, method, filtergraph_str, output_format, sufix]
    return ' '.join(temp_bucket)


def _generate_concat_files_list_option(parts):
    ''' parts are the file names with .mp4 you want to concat together
    '''
    inputs = ' '.join(parts)
    return "-safe 0 -i <(printf \"file '$PWD/%s'\\n\" " + inputs + ")"


def generate_concat_command_line(parts, result_file_name):
    ''' parts are the list of .mp4 file names '''
    program = 'ffmpeg -f concat'
    input_area = _generate_concat_files_list_option(parts)
    method = '-c copy %s' % result_file_name
    temp_bucket = [program, input_area, method]
    return ' '.join(temp_bucket)
