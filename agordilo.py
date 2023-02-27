#!/usr/bin/env python

import os
import torch
import subprocess
import re

# Write header comments in the configuration file
def write_header_comments(config_file):
    with open(config_file, "w") as f:
        f.write("# Configuration file for Wisper Connector\n")
        f.write("# This file is automatically generated by the Wisper Connector configuration tool\n")
        f.write("# You can edit this file to select the audio device and Wisper model. \n")
        f.write("\n")

# Get the default audio card using 'arecord -l` and write it to the configuration file
def get_default_device():
    try:
        output = subprocess.check_output(['arecord', '-l'], stderr=subprocess.STDOUT).decode()
        for line in output.split('\n'):
            if '*' in line:
                match = re.search(r'card (\d+): .*', line)
                if match:
                    return match.group(1)
    except subprocess.CalledProcessError as e:
        print('Could not get list of audio devices:', e.output.decode())

    return None

def write_audio_cards(config_file):
    # Write the entire output of `arecord -l` to the configuration file
    try:
        output = subprocess.check_output(['arecord', '-l'], stderr=subprocess.STDOUT).decode()
        with open(config_file, "a") as f:
            f.write("# Output of `arecord -l`\n")
            f.write("# Use the index of the desired audio device to set it as the default\n")
            f.write("# " + "\n# ".join(output.splitlines()) + "\n")
            # Get the default audio device
            default_audio_device = get_default_device()
            f.write("\n[SOUNDCARD]\n")
            if default_audio_device:
                f.write("default_audio_device = {}\n".format(default_audio_device))
                f.write("\n")
    except subprocess.CalledProcessError as e:
        print('Could not get list of audio devices:', e.output.decode())

# Set the default timeout to 900 seconds
def write_default_timeout(config_file):
    with open(config_file, "a") as f:
        f.write("# Default recording timeout in seconds, set to 0 to disable.\n")
        f.write("# If you speak longer than this without stoping,\n")
        f.write("# the recording will stop automatically, without transcribing.\n")
        f.write("# You can change this to any value you want\n")
        f.write("\n")
        f.write("[TIMEOUT]\n")
        f.write("timeout = 900\n")
        f.write("\n")

# Check VRAM and write list of available Wisper models
def write_wisper_models(config_file):
    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    with open(config_file, "a") as f:
        f.write("# Available VRAM: {:.2f} GB\n".format(total_memory))
        f.write("# List of available Wisper models\n")
        f.write("# Use the name of the desired Wisper model to set it as the default\n")
        f.write("# tiny: 39 M\n")
        f.write("# base: 74 M\n")
        f.write("# small: 244 M\n")
        f.write("# medium: 769 M\n")
        f.write("# large: 1550 M\n")
        f.write("\n")
        f.write("[MODEL]\n")
        if total_memory >= 5:
            f.write("default_model = medium.en\n")
        elif total_memory >= 2:
            f.write("default_model = small.en\n")
        elif total_memory >= 1:
            f.write("default_model = base.en\n")
        else:
            f.write("default_model = tiny.en\n")
        f.write("\n")

# Set the default data directory to ~/.local/share/whisper-typer-tool
def write_default_data_dir(config_file):
    with open(config_file, "a") as f:
        f.write("# Default data directory\n")
        f.write("# This is where the recordings and transcriptions are saved\n")
        f.write("# You can change this to any directory you want\n")
        f.write("# The directory will be created if it doesn't exist\n")
        f.write("# The directory must be writable by the user\n")
        f.write("\n")
        f.write("[DATA]\n")
        f.write("data_dir = ~/.local/share/whisper-typer-tool\n")
        f.write("\n")

# Define the path to the configuration file
config_file = os.path.expanduser("~/.config/whisper-typer-tool/config.txt")

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(config_file), exist_ok=True)

# Write the header comments and the list of available audio cards to the configuration file
write_header_comments(config_file)
write_audio_cards(config_file)
write_default_timeout(config_file)
write_wisper_models(config_file)
write_default_data_dir(config_file)