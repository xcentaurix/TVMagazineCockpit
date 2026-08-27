# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import os
import json
from six import text_type


def convert_unicode_to_str(input_data):
	if isinstance(input_data, dict):
		return {convert_unicode_to_str(key): convert_unicode_to_str(value) for key, value in input_data.iteritems()}
	if isinstance(input_data, list):
		return [convert_unicode_to_str(element) for element in input_data]
	if isinstance(input_data, text_type):
		return input_data.encode('utf-8')
	return input_data


def write_channel_list(bouquet, channel_list):
	channel_list_filename = "tvspielfilm_channel_list_%s.json" % bouquet
	path = channel_list_filename
	with open(path, 'w') as afile:
		json.dump(channel_list, afile, indent=2)


def read_channel_dict(channel_list=None, resolution="hd"):
	channel_dict = {}
	channel_list = channel_list if channel_list is not None else []
	filename = ""
	channel_dict_filename = "tvspielfilm_channel_dict_default.json"
	filename = channel_dict_filename
	sky_list = []
	if filename:
		with open(filename) as data_file:
			channels = convert_unicode_to_str(json.load(data_file))
			if channels:
				if not channel_list:
					channel_list = channels.keys()
				for channel_id in channel_list:
					if channel_id.startswith("SKY"):
						sky_list.append(channel_id)
	return sky_list

sky_list = read_channel_dict()
sky_list.sort()
write_channel_list("sky", sky_list)
