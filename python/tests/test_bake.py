from context import bake as bake # env of our project src

cake = [
	{
		'uid': '1.mp4',
		'start': '10',
		'end': '12',
		'filters': [
			{
				'name': 'vflip',
				'values': [],
				'kwvalues': {},
			},
		],
	},
	{
		'uid': '2.mp4',
		'start': '2',
		'end': '4',
		'filters': [
			{
				'name': 'hue',
				'values': [],
				'kwvalues': {'s':'0'},
			},
		],
	},
	{
		'uid': '3.mp4',
		'start': '16',
		'end': '18',
		'filters': [
			{
				'name': 'hflip',
				'values': [],
				'kwvalues': {},
			},
			{
				'name': 'crop',
				'values': [],
				'kwvalues': {'w':100,'h':200,'x':300,'y':400},
			},
		],
	},
]


def test_filter_adapter():
	assert bake.filter_adapter(cake[0]['filters'][0]) == 'vflip'
	assert bake.filter_adapter(cake[1]['filters'][0]) == 'hue=s=0'
	assert bake.filter_adapter(cake[2]['filters'][0]) == 'hflip'
	assert 'w=100' in bake.filter_adapter(cake[2]['filters'][1])
	assert 'h=200' in bake.filter_adapter(cake[2]['filters'][1])
	assert 'x=300' in bake.filter_adapter(cake[2]['filters'][1])
	assert 'y=400' in bake.filter_adapter(cake[2]['filters'][1])
	assert 'crop' in bake.filter_adapter(cake[2]['filters'][1])

def trim_filter_adapter():
	assert 'start_frame=10' in bake.trim_filter_adapter(cake[0])
	assert 'end_frame=12' in bake.trim_filter_adapter(cake[0])
	assert ':' in bake.trim_filter_adapter(cake[0])

def test_get_input_files():
	assert '1.mp4' in bake.get_input_files(cake)
	assert '2.mp4' in bake.get_input_files(cake)
	assert '3.mp4' in bake.get_input_files(cake)

def test_generate_filtergraph():
	assert len(bake.generate_filtergraph(cake,'myoutput')) == len(cake) * 2
	assert 'myoutput' in bake.generate_filtergraph(cake,'myoutput')[-1]

def test_generate_full_command_line():
	assert 'myresult.mp4' in bake.generate_full_command_line(cake,'myresult.mp4')