# tkpoint
Trackpoint configuration frontend for linux

I wrote this initially in bash/zenity and then rewrote it in python/tkinter so I could have real-time adjustment of settings, I am putting both out there for people to use or improve upon cause I have basically lost interest in further hacking on it. 

If you'd like to use or improve this or even use the rather simple approach as a template for other such tools, feel free to do so.

Both the bash and python versions are functional, and have similar functionality, only real differences are that the bash version due to limitations of zenity doesnt apply the settings in real time as you move the sliders, and does selection of more than one trackpoint device only if more than one is found and via a seperate step. With the python version there is realtime control and selection of device and provision in there for changing the widgets, range of the setting, and inputting description information for implementation of a sort of help dialog to show more information on each setting.
