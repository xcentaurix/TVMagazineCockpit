# enhance.py
import json
import os
import codecs  # For handling UTF-8 in Python 2.7

def read_tv_channels():
    """Read the tv_channels.json file from the current directory."""
    try:
        # Get the current directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the JSON file
        json_file_path = os.path.join(current_dir, 'tv_channels.json')
        
        # Open and read the JSON file (using codecs for Python 2.7)
        with codecs.open(json_file_path, 'r', encoding='utf-8') as file:
            channels_data = json.load(file)
            
        return channels_data
    
    except FileNotFoundError:
        print "Error: File 'tv_channels.json' not found in", current_dir
        return None
    except ValueError:  # Python 2.7 uses ValueError for JSON decode errors
        print "Error: The file contains invalid JSON"
        return None
    except Exception, e:  # Python 2.7 exception syntax
        print "An unexpected error occurred:", str(e)
        return None


def read_channel_dict():
    """Read the channel_dict.json file from the current directory."""
    try:
        # Get the current directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the JSON file
        json_file_path = os.path.join(current_dir, 'tvspielfilm_channel_dict_default.json')
        
        # Open and read the JSON file (using codecs for Python 2.7)
        with codecs.open(json_file_path, 'r', encoding='utf-8') as file:
            channel_dict_data = json.load(file)
            
        return channel_dict_data
    
    except FileNotFoundError:
        print "Error: File 'channel_dict.json' not found in", current_dir
        return None
    except ValueError:  # Python 2.7 uses ValueError for JSON decode errors
        print "Error: The file contains invalid JSON"
        return None
    except Exception, e:  # Python 2.7 exception syntax
        print "An unexpected error occurred:", str(e)
        return None


def parse_tv_channels(channels, channel_dict):
    """Parse the TV channels data."""
    
    for channel in channels:
        # Example parsing logic
        if "tvs_id" in channel and "tvfa_id" in channel:
            tvs_id = channel.get('tvs_id')
            tvfa_id = channel.get('tvfa_id')
            tvfa_name = channel.get('tvfa_name')
            if tvs_id and tvfa_id:
                for res in ["_sd", "_hd", "_uhd"]:
                    res_id = tvs_id + res
                    if res_id in channel_dict:
                        channel_dict[res_id]['tvfa_id'] = tvfa_id
                        channel_dict[res_id]['tvfa_name'] = tvfa_name
    return channel_dict


if __name__ == "__main__":
    # Execute when run as a script
    channels = read_tv_channels()
    
    if channels:
        print "Successfully loaded TV channels data:"
        # Pretty print the first few items to avoid overwhelming output
        # print json.dumps(channels[:5] if isinstance(channels, list) else channels, indent=2)
        
        if isinstance(channels, list):
            print "Total number of channels:", len(channels)
    
    channel_dict = read_channel_dict()
    
    if channel_dict:
        print "Successfully loaded channel dictionary data:"
        # Pretty print the first few items to avoid overwhelming output
        # print json.dumps(channel_dict[:5] if isinstance(channel_dict, list) else channel_dict, indent=2)
        
        if isinstance(channel_dict, list):
            print "Total number of channels in dictionary:", len(channel_dict)
    
    if channels and channel_dict:
        # Parse the TV channels and update the new dictionary
        new_dict = parse_tv_channels(channels, channel_dict)
        
        # Write the new dictionary to channel_dict.json
        try:
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Path to the output JSON file
            output_file_path = os.path.join(current_dir, 'tv_channel_dict.json')
            
            # Write the updated dictionary to the file
            with codecs.open(output_file_path, 'w', encoding='utf-8') as outfile:
                json.dump(new_dict, outfile, indent=4, ensure_ascii=False)
            
            print "Successfully wrote updated channel dictionary to channel_dict.json"
            print "File location:", output_file_path
            
        except Exception, e:
            print "Error writing to channel_dict.json:", str(e)
