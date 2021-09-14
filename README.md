# windfreak-pycontrol
Written with python2 and Qt4
Control windfreak device to lock laser frequency by tracking its wavelength on a wavemeter device.
Work nicely with wavemeters that is installed with a HTTP server to display the wavelengths.

This software has been around for a long time.
Currently, I have refactored the code a bit such that the program starts even without any available devices.
Would come back and do more cleaning up.

control_gui.py: the main app.

windfreakgui.ui: the Qt4 gui of the main app.

windfreak_control3.py: the cute library to talk to windfreak device written by Nick Lewty in 2014.
