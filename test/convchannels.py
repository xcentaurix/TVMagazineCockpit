# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0



import json
new_channels = []


def read_channels(resolution="hd"):
	filename = "channels.json"
	if filename:
		with open(filename) as data_file:
			org_channels = json.load(data_file, encoding='utf-8')
			if org_channels:
				for counter, org_channel in enumerate(org_channels):
					new_channel = org_channel + "_hd"
					new_channels.append(str(new_channel))

				print("%s channels" % counter)
				print(new_channels)

def write_channels():
	with open("new_channels.json", 'w') as fp:
		json.dump(new_channels, fp, indent=4)


read_channels()
write_channels()
