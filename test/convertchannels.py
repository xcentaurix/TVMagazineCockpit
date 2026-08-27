# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0



import json
new_channels = {}


def read_channels(resolution="hd"):
	filename = "org_channels.json"
	if filename:
		with open(filename) as data_file:
			data = json.load(data_file, encoding='utf-8')
			org_channels = data.get('channels')
			if org_channels:
				for counter, org_channel in enumerate(org_channels):
					print("0:", org_channel[0])
					print("1:", org_channel[1])
					print("\n")
					del org_channel[1]['id']
					new_channels[org_channel[0]] = org_channel[1]

				print("%s channels" % counter)
				for channel in new_channels:
					print(channel)
					print(new_channels[channel])

def write_channels():
	with open("tvspielfilm_default_channels.json", 'w') as fp:
		json.dump(new_channels, fp, indent=4)


read_channels()
write_channels()


