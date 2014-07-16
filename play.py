#!/usr/bin/env python
#
# Licensed under the BSD license.  See full license in LICENSE file.
# http://www.lightshowpi.com/
#
# Author: Todd Giles (todd@lightshowpi.com)
# Author: Chris Usey (chris.usey@gmail.com)
# Author: Ryan Jennings
# Author: Paul Dunn (dunnsept@gmail.com)
"""Play any audio file and synchronize lights to the music

Modified from original synchronized_lights.py
see original file for details

Sample usage:



Third party dependencies:

Lightshowpi must be installed, configured and working before this one will work
"""
#todo clean these up, not all are needed in this one pd
import argparse
import csv
import fcntl
import gzip
import logging
import os
import random
import sys
import time
import socket


from bootstrap import *
#need to move to config mgr
port = 8888

# Configurations - TODO(todd): Move more of this into configuration manager
led = LEDStrip(159)
led.fillRGB(255,0,0)
led.update()
led.all_off()

led_array = [0 for i in range(159)]


c = 0.0
columns = [1.0,1.0,1.0,1.0,1.0]
decay = .9  


#CHUNK_SIZE = 2048  # Use a multiple of 8



# TODO(todd): Refactor this to make it more readable / modular.
def main():
    '''main'''
   

try:
    # Initialize Lights
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(("192.168.1.91",port))
        print "Successfully bound port"
    except:
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("",port))
        print "Shutdown and bound port"
    test = 0
    trigger = 1
    while 1:
       
        led.fill(Color(0,0,0),0,151)
        
        
        

        for i in range(0,4):
       		
            
            #import data
            data, addr = s.recvfrom(2048)
            #split data
            col,height,c = data.split("=")
            color = wheel_color(int(c))
            #choose where to write out to
            if col == "0":        
                led.fill(color,0,int(height))
            elif col == "1":
                led.fill(color,63 - int(height),63)
            elif col == "2":
                led.fill(color,64,64+int(height))
            elif col == "3":
                led.fill(color,127- int(height),127)
            elif col == "4":
                led.fill(color,128,128+int(height))   
        #update LEDs
        led.update()
        

    
except KeyboardInterrupt:
        pass
finally:
        print "\nStopping"
        s.close()
    # We're done, turn it all off and clean up things ;)
    

if __name__ == "__main__":
    main()
