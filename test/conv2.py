# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0



import json
new_channels = {}


def read_channels(resolution="hd"):
	filename = "tvc_channel_dict.json"
	if filename:
		with open(filename) as data_file:
			org_channels = json.load(data_file, encoding='utf-8')
			if org_channels:
				for key, value in org_channels.items():
					channel = value
					if "tvfa_name" in channel:
						del channel["tvfa_name"]
					if "tvs_name" in channel:
						del channel["tvs_name"]
					if "tvm_name" in channel:
						del channel["tvm_name"]
					if "tvh_name" in channel:
						del channel["tvh_name"]
					new_channels[key] = channel
				print(new_channels)

def write_channels():
	with open("new_channels.json", 'w') as fp:
		json.dump(new_channels, fp, indent=4)


read_channels()
write_channels()
