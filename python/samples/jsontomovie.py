# read fcp-cakes from a json file,
# convert fcp-cake into a ffmpeg-cake
from context import translate as translate
from context import bake as bake
from context import jsonhelper as jsonhelper


def get_single_ffmpeg_cake(fcpcake):
    ''' input a dict obj, represents a fcp cake
    return a list obj, represents a ffmpeg cake
    '''
    cake_uid = fcpcake['cake_uid']
    cake_range_start = fcpcake['range_start']
    cake_range_end = fcpcake['range_end']

    layers = []
    for each in fcpcake['clips']:
        clip_delay_offset = each['offset']  # Clip Delay according to the base clip.
        layer = {}
        layer['resource'] = each['video']['ref']  # G
        layer['start'] = cake_range_start - clip_delay_offset  # G
        layer['end'] = cake_range_end - clip_delay_offset  # G
        layer['filters'] = [translate.translate_table.get(every) for every in each.keys() if 'adjust' in every]
        layer['filters'].extend([translate.translate_table.get(every) for every in each.keys() if 'filter' in every])
        layers.append(layer)

    return {'uid': cake_uid, 'layers': layers}


if __name__ == "__main__":
    grouped_fcp_cakes = jsonhelper.json_file_to_jsonobj('sample.json')

    ffmpeg_cakes = []  # The ffmpeg cakes ready to be put on the oven of ffmpeg to cook

    for each_cake_hash in grouped_fcp_cakes.keys():
        splitted_fcp_cakes = jsonhelper.split_ranges(each_cake_hash, grouped_fcp_cakes[each_cake_hash])
        for each_single_cake in splitted_fcp_cakes:
            ffmpeg_cakes.append(get_single_ffmpeg_cake(each_single_cake))

    render_commands = []  # Command line to execute one by one finally.
    movie_chunk_names = []  # Generated movie file names on the hard disk.
    for each_ffmpeg_cake in ffmpeg_cakes:
        output_file_name = '%s.mp4' % each_ffmpeg_cake['uid']
        render_commands.append(bake.generate_single_render_command_line(each_ffmpeg_cake, output_file_name))
        movie_chunk_names.append(output_file_name)

    render_commands.append(bake.generate_concat_command_line(movie_chunk_names, 'mixslice_movie.mp4'))
    # with open('sample.json', 'r') as f:
    #     json_string = ''.join(f.readlines())
    #     jsonobj = json.loads(json_string)

    #     fcpjson = jsonobj
    #     movie_parts = []  # container of temp generated movie file names
    #     render_commands = []  # command line to execute one by one finally
    #     for idx, each_cake in enumerate(fcpjson):
    #         output_file_name = 'test-part-%d.mp4' % idx
    #         ffmpeg_cake = get_single_ffmpeg_cake(each_cake)
    #         render_commands.append(bake.generate_single_render_command_line(ffmpeg_cake, output_file_name))
    #         movie_parts.append(output_file_name)

    #     render_commands.append(bake.generate_concat_command_line(movie_parts, 'mixslice_movie.mp4'))

    linked_render_commands = []
    for each in render_commands:
        temp = each.replace(' r2 ', ' WP_20140830_14_39_10_Pro.mp4 ').replace(' r3 ', ' WP_20140830_15_13_44_Pro.mp4 ')
        linked_render_commands.append(temp)

    render_commands = linked_render_commands
    import subprocess
    for each in render_commands[0:-1]:  # bake each ffmpeg cake into movie chunk
        print each
        print '-----------------'
        subprocess.call(each, shell=True)

    # join the movie parts together into a final movie.
    commandline = []
    commandline.append('/bin/bash')
    commandline.append('-c')
    commandline.append(render_commands[-1])
    child = subprocess.Popen(commandline)
