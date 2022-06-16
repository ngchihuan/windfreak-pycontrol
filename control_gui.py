#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Updated on 15th June 2022 to Python 3 and PyQt5
"""

import sys
import glob
import serial
import json
import urllib3
import windfreak_control3 as wc
from PyQt5 import QtGui, uic, QtCore, QtWidgets
import datetime
import time

form_class = uic.loadUiType("windfreakgui.ui")[0] 

def serial_ports():
    
    """Lists serial ports
    :raises EnvironmentError:
    On unsupported or unknown platforms
    :returns:
    A list of available serial ports
    """                
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]
    elif sys.platform.startswith('linux'):
    # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
        print(ports)
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    
    else:
        raise EnvironmentError('Unsupported platform')
    
    result = []
    for port in ports:
        print(port)
        try:
            #s = serial.Serial(port)
            s = serial.Serial(port, 115200, timeout=1)
            print(s)
            s.close()
            result.append(port)
        except serial.SerialException:
            pass
    print('result is')
    print(result)
    return result
    




class MyWindowClass(QtWidgets.QMainWindow, form_class):
    connected = bool(False)
    windfreak = None 
    time = 0
    UpdatedFreq = QtCore.pyqtSignal()

    #set_freq_timer.timeout.connect()


    
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.ButtonUpdate_freq.clicked.connect(self.FreqUpdate_Slot)
        self.ButtonUpdate_freq_2.clicked.connect(self.slowFreqUpdate_Slot)
        self.ButtonUpdate_power.clicked.connect(self.ButtonUpdate_power_clicked)
        self.ButtonUpdate_channel.clicked.connect(self.ButtonUpdate_channel_clicked)
        self.ButtonConnect.clicked.connect(self.ButtonConnect_clicked)
        self.ButtonUpdate_off.clicked.connect(self.ButtonUpdate_off_clicked)
        self.ButtonUpdate_on.clicked.connect(self.ButtonUpdate_on_clicked)
        self.pushButton_Up.clicked.connect(self.increaseby1_Slot)
        self.pushButton_Down.clicked.connect(self.decreaseby1_Slot)

        self.comboSerialBox.addItems(serial_ports()) #Gets a list of avaliable serial ports to connect to and adds to combo box

        self.set_freq_timer= QtCore.QTimer()
        self.set_freq_timer.timeout.connect(self.slowFreqUpdate)

        self.wavelength_check_timer = QtCore.QTimer()
        self.wavelength_check_timer.timeout.connect(self.updateWavemeterDisplay)
        self.wavelength_check_timer.start(10)

        self.set_lock_timer = QtCore.QTimer()
        self.set_lock_timer.timeout.connect(self.lock_process)

        self.ButtonLock.clicked.connect(self.lock_slot)

        self.lockStatus=False


    def updateFreq(self,freq):
        print('Set freq to '+ str(freq))
        self.windfreak.set_freq(freq)
        self.freq = float(self.windfreak.get_freq()) / 1000
        self.label_freq.setText(str(self.freq) + "MHz")
        #self.updateWavemeterDisplay()
        print ('freq is updated')
    
    def increaseby1_Slot(self):
        self.freq_current = float(self.windfreak.get_freq()) / 1000.0
        self.updateFreq(self.freq_current+1.0)
        self.freq_current = float(self.windfreak.get_freq()) / 1000.0
        self.freq_box.setValue(self.freq_current)

    def decreaseby1_Slot(self):
        self.freq_current = float(self.windfreak.get_freq()) / 1000.0
        self.updateFreq(self.freq_current-1.0)
        self.freq_box.setValue(self.freq_current)

    def ButtonConnect_clicked(self,connection):
        if not self.connected:
            self.windfreak = wc.windfreakusb2(str(self.comboSerialBox.currentText()))
            self.timer = QtCore.QTimer()
            self.connected = True
            self.timer.timeout.connect(self.update)
            self.timer.start(1000)
            self.control_label.setText('connected to ' + str(self.comboSerialBox.currentText()))
            self.freq = float(self.windfreak.get_freq())/1000
            self.power = self.windfreak.get_power()
            self.label_freq.setText(str(self.freq)+"MHz")
            self.label_power.setText(str(self.power))
            self.windfreak.set_clock(str(1)) #sets internal clock so that is locks
            self.windfreak.set_freq(str(self.freq))
            
    def FreqUpdate_Slot(self,value):
        self.updateFreq(self.freq_box.text())


    def slowFreqUpdate_Slot(self,value):
        self.timestep = float(self.time_box.text())
        self.set_freq_timer.start(int(self.timestep*100))
        # self.connect(self,SIGNAL("UpdatedFreq"),self.Pause_slowFreqUpdateSlot)
        self.UpdatedFreq.connect(self.Pause_slowFreqUpdateSlot)

    def Pause_slowFreqUpdateSlot(self):
        self.set_freq_timer.stop()
        self.ButtonUpdate_freq_2.setStyleSheet('QPushButton {color: black;}')
        self.ButtonUpdate_freq_2.setText('Update')
        self.ButtonUpdate_freq_2.clicked.connect(self.slowFreqUpdate_Slot)

    def slowFreqUpdate(self):
        #self.ButtonUpdate_freq_2.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.ButtonUpdate_freq_2.setStyleSheet('QPushButton {color: red;}')
        self.ButtonUpdate_freq_2.setText('Stop')
        self.ButtonUpdate_freq_2.clicked.connect(self.Pause_slowFreqUpdateSlot)
        self.freq_end = float(self.freq_box_2.text())
        self.freqstep = float(self.freq_box_3.text())
        self.freq_current = float(self.windfreak.get_freq())/1000.0
        #print(self.freq_end,self.freqstep,self.freq_current)

        if abs(self.freq_end - self.freq_current) <= self.freqstep:
            self.updateFreq((self.freq_end))
            print('Finishing Slowly Updating Freq')
            self.UpdatedFreq.emit()
        elif self.freq_end  > self.freq_current :
            self.updateFreq(self.freq_current + self.freqstep)
        elif  self.freq_end  < self.freq_current :
            self.updateFreq(self.freq_current - self.freqstep)



    def ButtonUpdate_off_clicked(self):        
        self.windfreak.rf_off()
        print ('device off')

    def ButtonUpdate_on_clicked(self):
                self.windfreak.rf_on()
                print ('device on')

    def ButtonUpdate_power_clicked(self,value):
        self.windfreak.set_power(self.power_box.text())
        self.power = self.windfreak.get_power()
        self.label_power.setText(self.power)
        print ('power updated')
    
    def ButtonUpdate_channel_clicked(self,value):
        
        url = "http://charsiew.qoptics.quantum.nus.edu.sg:8080" 
        try:
            urllib2.urlopen(url+"/switch_"+str(self.channel_box.text()))
        except:
            pass
        print ('channel updated')
        
        
    def updateWavemeterDisplay(self):
        url = "http://192.168.101.175:8000"
        try:
            url_data = (urllib2.urlopen(url + "/wavemeter.html"))
            t = url_data.read().split(',')
            self.wavelength=t[1]
        except:
            self.wavelength='Unavailable wavemeter'
        self.label_wavelength.setText(self.wavelength)

        '''
        url = "http://192.168.101.175:8000"
        self.data = json.load(urllib2.urlopen(url+"/data"))
        self.label_wavelength.setText(self.data['wavelength'])
        self.label_optical_freq.setText(self.data['freq'])
        self.label_channel.setText(self.data['channel'])
        '''

    def lock_slot(self):
        self.p = float(self.p_freq_lock.text()) * 10 ** 5  # P for wavelength lock. make it as a user setting in the future.
        # sign of p determine the polarity of the lock.
        self.falseValue = self.lockStatus
        self.lockStatus = not self.lockStatus

        self.ButtonUpdate_freq.setEnabled(self.falseValue)
        self.ButtonUpdate_freq_2.setEnabled(self.falseValue)
        self.pushButton_Up.setEnabled(self.falseValue)
        self.pushButton_Down.setEnabled(self.falseValue)
        #self.ButtonUpdate_freq.toggle()
        if self.lockStatus == True:
            self.prelockStatus = self.prelock_check()
            print(self.prelockStatus)
            self.change_lock_status(self.prelockStatus)
            if self.prelockStatus == True:
                self.set_lock_timer.start(100)
            else:
                self.change_lock_status(2)
        else:
            self.change_lock_status(False)
            self.set_lock_timer.stop()

    def change_lock_status(self,lock):
        if lock == False:
            self.ButtonLock.setStyleSheet('QPushButton {color: black;}')
            self.ButtonLock.setText('Lock')
        elif lock ==True:
            self.ButtonLock.setStyleSheet('QPushButton {color: red;}')
            self.ButtonLock.setText('Locked')
        elif lock==2:
            self.ButtonLock.setStyleSheet('QPushButton {color: red;}')
            self.ButtonLock.setText('Failed')
            time.sleep(1)
            self.ButtonLock.setStyleSheet('QPushButton {color: black;}')
            self.ButtonLock.setText('Lock')
    def lock_process(self):
        print("locking in progress")
        print(self.wavelength)

        self.freq_current = float(self.windfreak.get_freq())/1000.0
        self.wavelength_target = float(self.freq_lock_box.text())
        self.err_wavelength= float(self.wavelength) - self.wavelength_target
        
        if abs(self.err_wavelength) < 3E-5:

            self.EOMfreq = round(self.freq_current + self.p * self.err_wavelength,3)
            self.updateFreq(self.EOMfreq)

        if self.freq_current > float(self.freq_lock_max.text()):
            print("Exceed maximum allowed EOM freq")
            self.set_lock_timer.stop()

        if self.freq_current < float(self.freq_lock_min.text()):
            print("Below minimum allowed EOM freq")
            self.set_lock_timer.stop()

    def prelock_check(self):
        if self.wavelength == "Unavailable wavemeter":
            return False
        if float(self.wavelength) < float(self.freq_lock_box_min.text()) or float(self.wavelength) > float(self.freq_lock_box_max.text()) :
            return False
        return True

app = QtWidgets.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
