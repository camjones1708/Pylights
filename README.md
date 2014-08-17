Pylights
========

Repository for raspberry pi spectrum analyser sent from pc

Uses this library https://github.com/fishkingsin/elinux-lpd8806/

Project was started by Paul Dunn on here https://code.google.com/p/pc-pi-lightshow/

I also used https://learn.adafruit.com/downloads/pdf/raspberry-pi-spectrum-analyzer-display-on-rgb-led-strip.pdf
by Scott Driscoll as a large reference and a lot of material of the lightshowpi community.

Credit to Sean Millar, Todd Giles, and Chris Usey as well for their lightshowpi work.

I ran by using IDLE on my desktop PC to run stereomix.py, you may need to change your device depending on what device your stereomix is. Paul Dunn's page has more documentation on this as this file is his as well as the audiodevice.py file.

Then on my desktop I used the makefile provided by the library so I had my .c file named simple_example.c to replace the current and ran the following commands:

make simple_example
./simple_example

That should do the trick. You will have to change IP Addresses for your needs. When I go back, I will comment the code.
