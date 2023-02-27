from pynput import keyboard
import codecs
import whisper
import time
import subprocess
import threading
import wave
import os
from playsound import playsound
from datetime import datetime
import configparser
import queue
import sys
import subprocess
import signal

# Import the configuration file
config_file = os.path.expanduser("~/.config/whisper-typer-tool/config.txt")
config = configparser.ConfigParser()
config.read(config_file)

# Get the default model
default_model = config["MODEL"]["default_model"]

# Get the default audio device
default_audio_device = int(config["SOUNDCARD"]["default_audio_device"])

# Get the default timeout
default_time_to_record = int(config["TIMEOUT"]["timeout"])

# Get the data directory
data_dir = config["DATA"]["data_dir"]

# Create the data directory if it doesn't exist
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

#ready counter
file_ready_counter=1

#recording variables
is_recording = False
is_sound_test = False
record_process = None
filename = None

#load model
print("loading model...")
model = whisper.load_model(default_model)
#playsound("model_loaded.wav")
print(f"{default_model} model loaded")

#function to transcribe speech
def record_audio(filename):
    global record_process
    global is_recording
    is_recording = True
    record_process = subprocess.Popen(['arecord', '-D', 'plughw:'+str(default_audio_device)+',0',
                    '-f', 'S16_LE', '-r', '44100', '-d', str(default_time_to_record), filename])

def stop_recording():
    global record_process
    global is_recording
    is_recording = False
    os.kill(record_process.pid, signal.SIGINT)

def transcribe_speech(queue):
    print("Ready - start transcribing with F2 ...\n")
    while True:
        filename = queue.get()
        result = model.transcribe(os.path.join(data_dir, filename))
        print(result["text"]+"\n")
        now = str(datetime.now()).split(".")[0]
        with codecs.open(os.path.join(data_dir, 'transcribe.log'), 'a', encoding='utf-8') as f:
            f.write(now+" : "+result["text"]+"\n")
        for element in result["text"]:
            try:
                keyboard.type(element)
                time.sleep(0.0025)
            except:
                pass
        os.remove(os.path.join(data_dir, filename))

def toggle_recording():
    global is_recording
    global file_ready_counter
    global filename
    now = datetime.now()

    if is_recording:
        # stop recording
        stop_recording()
        queue.put(filename)
        print("Stop recording key pressed...\n")
    else:
        # start recording
        file_ready_counter += 1
        filename = now.strftime("%Y-%m-%d-%H-%M-%S") + " counter: " + str(file_ready_counter) + ".wav"
        record_audio(os.path.join(data_dir, filename))
        print("Start recording key pressed...\n")

# transcribe speech in infinite loop
queue = queue.Queue()
t2 = threading.Thread(target=transcribe_speech, args=(queue,))
t2.start()

#hot key events
def on_release(key):
    global is_recording
    global is_sound_test

    if key == keyboard.Key.f2 and not is_sound_test:
        toggle_recording()
    elif key == keyboard.Key.f4:
        if is_recording and is_sound_test:
            stop_recording()
            is_sound_test = False
            filename = "test" + str(file_ready_counter) + ".wav"
            subprocess.Popen(["aplay", os.path.join(data_dir, filename)])
        elif is_recording and not is_sound_test:
            pass
        else:
            is_sound_test = True
            filename = "test" + str(file_ready_counter) + ".wav"
            record_audio(os.path.join(data_dir, filename))
            print("Speak into the microphone.\n Press the test key again, to hear your audio test.\n")
    elif key == keyboard.Key.esc:
        if is_recording:
            toggle_recording()
        print("Exiting...\n")
        os._exit(0)

with keyboard.Listener(on_release=on_release) as listener:
    listener.join()
