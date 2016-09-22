# read fcp-cakes from a json file,
# convert fcp-cake into a ffmpeg-cake
import json
from context import translate as translate
from context import bake as bake


def get_single_ffmpeg_cake(fcpcake):
    ''' input a dict obj, represents a fcp cake
    return a list obj, represents a ffmpeg cake
    '''
    cake_hash = fcpcake.keys()[0]
    cake_duration = fcpcake[cake_hash]['$']['duration']
    layers = []
    for each in fcpcake[cake_hash]['clips']:
        layer = {}
        layer['uid'] = each['video']['$']['ref']
        layer['start'] = each['start']
        layer['end'] = each['start'] + cake_duration
        layer['filters'] = [translate.translate_table.get(every) for every in each.keys() if 'adjust' in every]
        layer['filters'].extend([translate.translate_table.get(every) for every in each.keys() if 'filter' in every])
        layers.append(layer)

    return {'uid': cake_hash, 'layers': layers}


with open('sample.json', 'r') as f:
    json_string = ''.join(f.readlines())
    jsonobj = json.loads(json_string)

    fcpjson = jsonobj
    movie_parts = []
    for idx, each_cake in enumerate(fcpjson):
        output_file_name = 'test-part-%d.mp4' % idx
        ffmpeg_cake = get_single_ffmpeg_cake(each_cake)
        print bake.generate_full_command_line(ffmpeg_cake, output_file_name)
        movie_parts.append(output_file_name)

    print bake.concat_all_movie_parts(movie_parts, 'mixslice_movie.mp4')
