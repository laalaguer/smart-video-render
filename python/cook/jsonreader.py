# read fcp-cakes from a json file,
# convert fcp-cake into a ffmpeg-cake
import json
import translate
import bake


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
        layers.append(layer)

    return {'uid': cake_hash, 'layers': layers}


with open('sample.json', 'r') as f:
    json_string = ''.join(f.readlines())
    jsonobj = json.loads(json_string)

    fcpjson = jsonobj
    for each_cake in fcpjson:
        ffmpeg_cake = get_single_ffmpeg_cake(each_cake)
        print bake.generate_full_command_line(ffmpeg_cake, 'test.mp4')
