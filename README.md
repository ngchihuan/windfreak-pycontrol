# Introduction
This repository has been forked from https://github.com/ngchihuan/windfreak-pycontrol and updated to run on Python 3 and PyQt5 instead, as the original runs on Python 2 and PyQt4.

This software can be used to lock the frequency of a laser using wavemeter as a reference.
The feedback loop is done by fetching a wavemeter reading and control the frequency of a RF device, in this case the Windfreak. The current version only supports SynthUSBII: 34MHz – 4.4GHz USB RF Signal Generator. (For more information, [https://windfreaktech.com/product/usb-rf-signal-generator/](https://windfreaktech.com/product/usb-rf-signal-generator/)).

Currently, I have refactored the code a bit such that the program starts even without any available devices.
I would come back and do more cleaning up.

The GUI of the software is shown here

![Alt text](gui.png?raw=true "GUI")

# Installation and Dependencies

For now, there is no wheels or docker files that can provide a smooth installation.
Users can clone the project from github: [https://github.com/ngchihuan/windfreak-pycontrol.git](https://github.com/ngchihuan/windfreak-pycontrol.git) and run the software using terminal command`python2 control_gui.py`.

Dependencies: 

Python2 and its builtin libraries. 

`PyQt4==4.11.4`

`pyserial==3.5`

Note that PyQt4 installations can be problematic.

# Quick start

Run the software using terminal command`python2 control_gui.py` 

Step 1. Choose the windfreak device using the drop list which shows available devices listed as serial devices in linux.

Step 2. Click `connect to the windfreak`. `Controller status` is shown on the top left corner. 

Step 3. Set the frequencies, power and channel. The second row `Set Freq` can be used to ramp up/down the frequencies slowly.

Step 4. `Device on` to turn on 

Step 5 (Optional): Set the target wavelength and click the button`LOCK`. if the Locking is successful, the button would change to `LOCKED`

# File Description

`control_gui.py`: the main app.

`windfreakgui.ui`: the Qt4 gui of the main app.

`windfreak_control3.py`: acute library used to send commands to windfreak devices written by Nick Lewty in 2014.

# Issues and feature requests

Potential issues include occasional freezing during the ramp up and down of frequency. 
Any other issues and suggestions can be posted to the github issue section of this repo.
