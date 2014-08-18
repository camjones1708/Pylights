""" from lightshowpi synchronized_lights
You must have python 2.7, numpy and pyaudio installed for this to function
You must first enable stereo mix on windows and then run audiodevices.py to
find the device number for stereo mix.
Then edit this file and set the line

device=1
to match your device number.
The PC and your raspberry pi must be on the same network for this to function
as the data is streamed UDP on port 8888 as defined below

Once you have everything configured, start playing media on the PC and then start this
python, you will see a print-out of the frequencies used for the channels
then start play.py on the raspberry as sudo

# Author: Todd Giles (todd@lightshowpi.com)
# Author: Chris Usey (chris.usey@gmail.com)
# Author: Ryan Jennings
# Author: Paul Dunn (dunnsept@gmail.com) - move to PC

TODO lots and lots of clean-up and re-integration to lightshow pi
"""
import pyaudio # from http://people.csail.mit.edu/hubert/pyaudio/
import sys
import math
import numpy as np
import socket
import json

#todo move config to config manager
port=8888

#edit this to match your stereo mix device
device = 1

CHUNK_SIZE = 1024
GPIOLEN = 5
sample_rate = 44100
min_frequency = 20
max_frequency = 13000
_CUSTOM_CHANNEL_FREQUENCIES = 0
_CUSTOM_CHANNEL_MAPPING = 0
matrix    = [0,0,0,0,0,0,0,0]
height = [0,0,0,0,0]
col = 0

columns = [1.0,1.0,1.0,1.0,1.0]
decay = .9
# this writes out light and color information to a continuous RGB LED
# strip that's been wrapped around into 5 columns.
# numbers comes in at 9-15 ish

def json_list(list):
    lst = []
    for pn in list:
        lst.append(pn)
    return json.dumps(lst)

def display_column(col=0,height=0.0):
	global c
	global columns
	height = height - 8.0
	height = height / 5
	if height < .05:
		height = .05
	elif height > 1.0:
		height = 1.0
		
	if height < columns[col]:
		columns[col] = columns[col] * decay
		height = columns[col]
	else:
		columns[col] = height
	return(height)


def piff(val, sample_rate):
    '''Return the power array index corresponding to a particular frequency.'''
    return int(CHUNK_SIZE * val / sample_rate)

# TODO(todd): Move FFT related code into separate file as a library
def calculate_levels(data, sample_rate, frequency_limits):
    '''Calculate frequency response for each channel

    Initial FFT code inspired from the code posted here:
    http://www.raspberrypi.org/phpBB3/viewtopic.php?t=35838&p=454041

    Optimizations from work by Scott Driscoll:
    http://www.instructables.com/id/Raspberry-Pi-Spectrum-Analyzer-with-RGB-LED-Strip-/
    '''

    # create a numpy array. This won't work with a mono file, stereo only.
    data_stereo = np.frombuffer(data, dtype=np.int16)
    data = np.empty(len(data) / 4)  # data has two channels and 2 bytes per channel
    data[:] = data_stereo[::2]  # pull out the even values, just using left channel

    # if you take an FFT of a chunk of audio, the edges will look like
    # super high frequency cutoffs. Applying a window tapers the edges
    # of each end of the chunk down to zero.
    window = np.hanning(len(data))
    data = data * window

    # Apply FFT - real data
    fourier = np.fft.rfft(data)

    # Remove last element in array to make it the same size as CHUNK_SIZE
    fourier = np.delete(fourier, len(fourier) - 1)

    # Calculate the power spectrum
    power = np.abs(fourier) ** 2

    matrix = [0 for i in range(GPIOLEN)]
    for i in range(GPIOLEN):
        # take the log10 of the resulting sum to approximate how human ears perceive sound levels
        matrix[i] = np.log10(np.sum(power[piff(frequency_limits[i][0], sample_rate)
                                          :piff(frequency_limits[i][1], sample_rate):1]))

    return matrix

def stereomix_show():

#CHANGE THIS TO CORRECT INPUT DEVICE
# Enable stereo mix on your sound card
    host = ''
    BACKLOG = 5
    c = 0
    p = pyaudio.PyAudio()
    pyaudio.paDirectSound = 1
    stream = p.open(format = pyaudio.paInt16,
    channels = 2,
    rate = 44100,
    input = True,
    frames_per_buffer = CHUNK_SIZE,
    input_device_index = device)

    #setup UDP broadcast socket
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #s.bind((host,port))
    #err = s.listen(BACKLOG)
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
    mean = [12.0 for _ in range(GPIOLEN)]
    std = [1.5 for _ in range(GPIOLEN)]
    print "Connection accepted"
    try:
        
        frequency_limits = calculate_channel_frequency(20,15000,0,0)
        print frequency_limits
        while True:
            #client,address = s.accept()
            data = stream.read(CHUNK_SIZE)
            matrix = calculate_levels(data, sample_rate, frequency_limits)
            data = []
            
            for i in range(0, GPIOLEN):
                c = c + .1
                if c > 384:
                    c = 0.0
            # Calculate output pwm, where off is at 0.5 std below the mean
            # and full on is at 0.75 std above the mean.
                
                height[i] =  int(round(display_column(i,matrix[i])*31))
                #data.append(int(round(height*31)))
            #data = json_list(data)
            data = str(height[0]) + "," + str(height[1]) + "," + str(height[2]) + "," + str(height[3]) + "," + str(height[4])
            print data
            s.sendto(data, ("192.168.1.100",port))
            
                #uncomment line below if you want to see the 'data' being streamed
    except KeyboardInterrupt:
        pass
    finally:
        print "\nStopping"
        stream.close()
        p.terminate()

def calculate_channel_frequency(min_frequency, max_frequency, custom_channel_mapping, custom_channel_frequencies):
    '''Calculate frequency values for each channel, taking into account custom settings.'''

    # How many channels do we need to calculate the frequency for
    channel_length = GPIOLEN

   # logging.debug("Calculating frequencies for %d channels.", channel_length)
    octaves = (np.log(max_frequency / min_frequency)) / np.log(2)
   # logging.debug("octaves in selected frequency range ... %s", octaves)
    octaves_per_channel = octaves / channel_length
    frequency_limits = []
    frequency_store = []

    frequency_limits.append(min_frequency)
    if custom_channel_frequencies != 0 and (len(custom_channel_frequencies) >= channel_length + 1):
      
        frequency_limits = custom_channel_frequencies
    else:
      
        for i in range(1, GPIOLEN + 1):
            frequency_limits.append(frequency_limits[-1]
                                    * 10 ** (3 / (10 * (1 / octaves_per_channel))))
    for i in range(0, channel_length):
        frequency_store.append((frequency_limits[i], frequency_limits[i + 1]))
       

    # we have the frequencies now lets map them if custom mapping is defined
    if custom_channel_mapping != 0 and len(custom_channel_mapping) == GPIOLEN:
        frequency_map = []
        for i in range(0, GPIOLEN):
            mapped_channel = custom_channel_mapping[i] - 1
            mapped_frequency_set = frequency_store[mapped_channel]
            mapped_frequency_set_low = mapped_frequency_set[0]
            mapped_frequency_set_high = mapped_frequency_set[1]
            
            frequency_map.append(mapped_frequency_set)
        return frequency_map
    else:
        return frequency_store
    
if __name__ == '__main__':
#list_devices()
    stereomix_show()
