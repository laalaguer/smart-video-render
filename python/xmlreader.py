# Read XML from Final Cut Pro xml file.
# Generate a sequence timeline object for testing purpose.

import xml.etree.ElementTree as ET


# def get_asset(filename):
# 	''' Get a dict of r1:{uid:xxx,src:xxx}'''
# 	tree = ET.parse(filename)
# 	root = tree.getroot()
	


def get_timeline_clips(filename):
	''' input a fcpxml, output a [] full of clips and information about them
	'''
	result = [] # return list, each item is a lane, each lane contains clips

	tree = ET.parse(filename)
	root = tree.getroot()
	mainlane_clips = root.findall('./library/event/project/sequence/spine/clip')
	for each in mainlane_clips:
		each.attrib['lane'] = 0

	sublane_clips = []
	for each_main_clip in mainlane_clips:
		sub_clips = each_main_clip.findall('clip')
		for each in sub_clips:
			each.attrib['lane'] = int(each.attrib['lane'])
			each.attrib['parent_offset'] = each_main_clip.attrib['offset']
		sublane_clips.extend(sub_clips)
	
	result.extend([each.attrib for each in mainlane_clips])
	result.extend([each.attrib for each in sublane_clips])

	return result