# 
#
#  Sixfab Setup and Diagnostic Tool  
#  2020
#
#

import os
import requests 
import json
import subprocess
import sys
import time
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import *
from pathlib import Path
from urllib.request import urlopen  
import RPi.GPIO as GPIO
import serial
from serial import Serial
import logging


GPIO.setmode(GPIO.BCM)
logging.basicConfig(filename='setup-and-diagnostic-tool.log', format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s: - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

form = resource_path("setup_and_diagnostic_tool.ui")
Ui_MainWindow, QtBaseClass = uic.loadUiType(form)

"""
try:
    form = resource_path("setup_and_diagnostic_tool.ui")
    Ui_MainWindow, QtBaseClass = uic.loadUiType(form)
except Exception as e:
    logging.error("resource_path error - Ui_MainWindow, QtBaseClass", exc_info=True)
"""
TIME_LIMIT = 100
def assignment(text):
    if(text=="GSM/GPRS Shield"):
        return "1"
    elif(text=="Base Shield"):
        return "2"
    elif(text=="CellularIoT Shield"):
        return "3"
    elif(text=="CellularIoT HAT"):
        return "4"
    elif(text=="Tracker HAT"):
        return "5"
    elif(text=="Base HAT"):
        return "6"

def sendPing(text):
    connect=True
    if(text=="qmi"):
        ping  = os.popen('ping -I wwan0 -c 5 8.8.8.8').readlines()
    elif(text=="ppp"):
        ping  = os.popen('ping -I ppp0 -c 5 8.8.8.8').readlines()
    else:
        logging.info("Ping sending failed.")

    for i in range(len(ping)):
        packet = ping[i]
        control = packet.find("100% packet loss")
        if(control != -1):
            connect=False
            break
    if(connect==False):
        return "Internet connection failed." # "Interface found"
    else:
        return "Connection established."

def internet_check():
    try:
        response = urlopen('https://www.google.com/', timeout=10)
        return True
    except: 
        return False

def sendATcommand(command):
    try:
        port =serial.Serial("/dev/ttyUSB2", baudrate=115200, timeout=1)
    except Exception as e:
        logging.error("Serial port connection failed.", exc_info=True)
        logging.error("sendATcommand function was not executed", exc_info=True)
    port.write((command+'\r\n').encode())
    receive= port.read(100).decode()
    var = receive.splitlines()
    var = list(filter(None, var))
    logging.info(var)
    if(len(var)!=1):
        for i in var:
            if(i==command):
                del var[var.index(command)]
            elif(i=='OK'):
                del var[var.index('OK')]
    else:
        logging.info("...")
        #del var[0]
    toString = ' '.join(map(str, var))
    logging.info(toString)
    return toString

class DesktopTool(QMainWindow):
    def __init__(self):
        super(DesktopTool, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
    ###                         ### 
    ###                         ### 
    ###       MAIN DESIGN       ### 
    ###                         ### 
    ###                         ### 
        self.ui.installer.setVisible(False)
        self.ui.diagnostic.setVisible(False)
        self.ui.label.setVisible(False)
        self.ui.diagnostic_button.clicked.connect(self.onDiagnostic)
        self.ui.installer_button.clicked.connect(self.onInstaller)
        self.ui.main_button.clicked.connect(self.onMain)

    ###                         ### 
    ###                         ### 
    ###    INSTALLER DESIGN     ### 
    ###                         ### 
    ###                         ###

    #header_label
    #graphicsView // Sixfab Logo
    # Service
        #select_label
        try:
            self.ui.select_service_comboBox.addItem("")
            self.ui.select_service_comboBox.addItem("QMI")
            self.ui.select_service_comboBox.addItem("PPP")
            self.ui.select_service_comboBox.activated[str].connect(self.onSelectservice)
        except Exception as e:
            logging.error("onSelectservice function was not executed", exc_info=True)
    # Shield/Hat

    # GroupBox
        self.ui.qmi_groupBox.setVisible(False)
        self.ui.ppp_groupBox.setVisible(False)
        
        #self.ui.route_frame.setVisible(False)
        
    ###                         ### 
    ###                         ### 
    ###        QMI DESIGN       ### 
    ###                         ### 
    ###                         ### 
    
    # Detect board type
        command = 'cat /proc/device-tree/model'
        model = os.popen(command).read().strip()
        if model.lower().find('raspberry pi 4') > -1:
            self.ui.kernelButton.setEnabled(False)
            self.ui.progressBar_2.setValue(100)
            
    
    #Step 1
        #try:
            #self.ui.updateButton.clicked.connect(self.onUpdateButtonClick) # Button in step 1 - Update & Upgrade 
            #self.ui.progressBar.setVisible(True) # ProgressBar
        #except Exception as e:
        #    logging.error("onUpdateButtonClick function was not executed", exc_info=True)
    #Step 2
        try:
            self.ui.kernelButton.clicked.connect(self.onKernelButtonClick) # Button in step 2 - rpi-update & Github API
            #self.ui.progressBar_2.setVisible(True) # ProgressBar
        except Exception as e:
            logging.error("onKernelButtonClick function was not executed", exc_info=True)
    #Step 3
        try:
            self.ui.scriptButton.clicked.connect(self.onScriptButtonClick) # Button in step 4 - qmi_install.sh
            #self.ui.progressBar_3.setVisible(True) # ProgressBar
        except Exception as e:
            logging.error("onScriptButtonClick function was not executed", exc_info=True)
    #Step 4
        try:
            #self.ui.apn_label.setVisible(True) # QLabel - Text: "APN:"
            #self.ui.qmi_apn.setVisible(True) # QLineEdit - Input APN
            self.ui.serviceButton.clicked.connect(self.onServiceButtonClick) # Button in step 6 - QMI service active
            self.ui.qmi_status_label.setVisible(False) # QLabel - QMI service status
        except Exception as e:
            logging.error("onServiceButtonClick function was not executed", exc_info=True)
    #Step 5
        try:
            self.ui.testButton.clicked.connect(self.onTestButtonClick) # Button in step 7 - QMI test internet
            self.ui.qmi_test_label.setVisible(False) # QLabel - QMI test internet 
        except Exception as e:
            logging.error("onTestButtonClick function was not executed", exc_info=True)
    #Step 6
        try:
            self.ui.qmi_autoConnect_check.stateChanged.connect(self.state_changed) # QCheckBox - Qmi auto connect control
        except Exception as e:
            logging.error("state_changed function was not executed", exc_info=True)
        #self.ui.apn_label_2.setVisible(False) # QLabel - Text: "APN:" 
        #self.ui.qmi_apn_auto.setVisible(False) # QLineEdit - Input APN
        try:    
            self.ui.autoButton.clicked.connect(self.onAutoButtonClick) # Button in step 8 - QMI auto connect
        except Exception as e:
            logging.error("onAutoButtonClick function was not executed", exc_info=True)
        self.ui.autoButton.setVisible(False) # Button in step 8
        self.ui.qmi_auto_label.setVisible(False)
        
    ###                         ### 
    ###                         ### 
    ###        PPP DESIGN       ### 
    ###                         ### 
    ###                         ### 
    
    #Step 1
        #self.ui.apn_label_3.setVisible(True) # QLabel - Text: "What is your carrier APN? :"
        #self.ui.ppp_apn.setVisible(True) # QLabel - Input APN
    #Step 2
        #self.ui.port_label.setVisible(True) # QLabel - Port
        self.ui.ppp_port_comboBox.addItem("")
        self.ui.ppp_port_comboBox.addItem("ttyS0")
        self.ui.ppp_port_comboBox.addItem("ttyUSB3")
        
    #Step 3
        #self.ui.autoConnect_label.setVisible(True) # QLabel - Text: "Do you want to activate auto-connect? :" 
        self.ui.ppp_auto_comboBox.addItem("")
        self.ui.ppp_auto_comboBox.addItem("Yes")
        self.ui.ppp_auto_comboBox.addItem("No")

    #Other 
        try:        
            self.ui.pppInstallButton.clicked.connect(self.onPPPInstallButton) # Install & Reboot button
        except Exception as e:
            logging.error("onPPPInstallButton function was not executed", exc_info=True)
        try:
            self.ui.pppTestButton.clicked.connect(self.onPPPTestButton) # PPP test internet
        except Exception as e:
            logging.error("onPPPTestButton function was not executed", exc_info=True)
        self.ui.ppp_test_label.setVisible(False) # QLabel - PPP test internet 

    #Credential Frame
        self.ui.credential_checkBox.stateChanged.connect(self.credential_changed) # Outside the frame
        self.ui.credential_frame.setVisible(False)
        #username_label
        #username
        #password_label
        self.ui.password.setEchoMode(QLineEdit.Password)
        self.ui.show_checkBox.stateChanged.connect(self.password_changed)
        try:
            self.ui.addCredential.clicked.connect(self.onAddCredentialButton)
        except Exception as e:
            logging.error("onAddCredentialButton function was not executed", exc_info=True)


    ###                         ### 
    ###                         ### 
    ###   DIAGNOSTIC  DESIGN    ### 
    ###                         ### 
    ###                         ### 
        self.ui.dig_hat_shield_combobox.setVisible(False)
        self.ui.dig_hat_shield_combobox.addItem("")
        self.ui.dig_hat_shield_combobox.addItem("Base HAT")
        self.ui.dig_hat_shield_combobox.addItem("Base Shield")
        self.ui.dig_hat_shield_combobox.addItem("CellularIoT HAT")
        self.ui.dig_hat_shield_combobox.addItem("CellularIoT Shield")
        self.ui.dig_hat_shield_combobox.addItem("GPS Tracker HAT")
        self.ui.dig_detection_label.setVisible(False)
        try:
            self.ui.dig_diagnostic_button.clicked.connect(self.onDiagnose)  # Diagnose Button
        except Exception as e:
            logging.error("onDiagnose function was not executed", exc_info=True)


    ###                         ### 
    ###                         ### 
    ###        INSTALLER        ### 
    ###                         ### 
    ###                         ###   
        try:  
            if(os.path.isdir("/var/lib/sixfab")!=True or os.path.exists("/var/lib/sixfab/sixfab-status")!=True):
                os.system("sudo mkdir /var/lib/sixfab")  
                os.system("sudo touch /var/lib/sixfab/sixfab-status")
                os.system("sudo chmod a+rwx /var/lib/sixfab/sixfab-status")
        except Exception as e:
            logging.error("sixfab-status file error", exc_info=True)
        """
        try:
            if(os.path.isdir("/etc/ppp/peers")!=True or os.path.exists("/etc/ppp/peers/provider")!=True):
                os.system("sudo mkdir /etc/ppp/peers")
                os.system("sudo touch /etc/ppp/peers/provider")
                os.system("sudo chmod a+rwx /etc/ppp/peers/provider")
        except Exception as e:
            logging.error("/etc/ppp/peers/provider file error", exc_info=True)
        """
        try:
            if(os.path.exists("/var/lib/sixfab/sixfab-status")):
                logging.info("Sixfab status: -exists- ")
                with open("/var/lib/sixfab/sixfab-status","r",encoding = "utf-8") as f:
                    a=f.readlines()
                    logging.info("Sixfab status: "+ a[0])
                    if(len(a)==0):
                        logging.info("Sixfab status: Empty array")
                    elif(a[0]=='1'):
                        logging.info("Sixfab status: "+ a[0])
                        #self.ui.progressBar.setValue(100)
                    elif(a[0]=='2'):
                        logging.info("Sixfab status: "+ a[0])
                        #self.ui.progressBar.setValue(100)
                        self.ui.progressBar_2.setValue(100)
                    elif(a[0]=='3'):
                        logging.info("Sixfab status: "+ a[0])
                        #self.ui.progressBar.setValue(100)
                        self.ui.progressBar_2.setValue(100)
                        self.ui.progressBar_3.setValue(100)
            else:
                logging.info("Sixfab-status Not Found")
                print("Sixfab-status Not Found")
        except Exception as e:
            logging.error("sixfab-status file error", exc_info=True)

    ###                         ### 
    ###                         ### 
    ###       DIAGNOSTIC        ### 
    ###                         ### 
    ###                         ### 
        if(os.path.exists("/proc/device-tree/hat")): ##/proc/device-tree/hat
            f=open("/proc/device-tree/hat/product", "r")
            hat=f.read().splitlines()
            f.close()
            f=open("/proc/device-tree/hat/product_id", "r")
            product_id = f.read().splitlines()
            f.close()
            product_id = product_id[0].rsplit('\x00')
            logging.info(hat)
            logging.info(hat[0])
            self.ui.dig_detection_label.setVisible(True)
            self.ui.shield_hat_comboBox.setVisible(False)
            self.ui.label.setVisible(True)
            self.ui.label.setText(hat[0])
            self.ui.dig_detection_label.setText(hat[0])
            if( product_id[0] == '0x0003'):
                if(os.path.exists("/dev/ttyUSB0") and os.path.exists("/dev/ttyUSB1") and os.path.exists("/dev/ttyUSB2") and os.path.exists("/dev/ttyUSB3")):
                    self.ui.dig_connect_label.setText("Module: Ready!")
                else:
                    self.ui.dig_connect_label.setText("Module: Not ready, check power of module.")
            elif(product_id == "0x0001" or product_id == "0x0004"):
                STATUS = 23
                GPIO.setup(STATUS, GPIO.IN)
                #if(STATUS==23):
                if(GPIO.input(STATUS)):
                    self.ui.dig_connect_label.setText("Module: Ready!")
                else:
                    self.ui.dig_connect_label.setText("Module: Not ready, check power of module.")
            else:
                self.ui.dig_connect_label.setText("HAT detected but something went wrong.")
                logging.info("HAT detected but something went wrong.")
        else:
            self.ui.dig_hat_shield_combobox.setVisible(True)
            
        try:
            self.ui.dig_hat_shield_combobox.activated[str].connect(self.onStatus)
        except Exception as e:
            logging.error("onStatus function was not executed.", exc_info=True)

### --------------- ###                
#       
#      FUNCTIONS 
#                
### ---------------###

    def onStatus(self,text):
        print(text)
        if(text=="Base HAT" or text=="Base Shield"):
            if(os.path.exists("/dev/ttyUSB0") and os.path.exists("/dev/ttyUSB1") and os.path.exists("/dev/ttyUSB2") and os.path.exists("/dev/ttyUSB3")):
                self.ui.dig_connect_label.setText("Module: Ready!")
                logging.info("Module: Ready!")
            else:
                self.ui.dig_connect_label.setText("Module: Not ready, check power of module.")
                logging.info("Module: Not ready, check power of module.")
                
        elif(text=="CellularIoT HAT" or text=="GPS Tracker HAT"):
            STATUS = 23
            GPIO.setup(STATUS, GPIO.IN)
            #if(STATUS==23):
            if(GPIO.input(STATUS)):
                self.ui.dig_connect_label.setText("Module: Ready!")
                logging.info("Module: Ready! - Cellular HAT - Tracker HAT")
            else:
                self.ui.dig_connect_label.setText("Module: Not ready, check power of module.")
                logging.info("Module: Not ready, check power of module. - Cellular HAT - Tracker HAT")
        elif(text=="CellularIoT Shield"):
            STATUS = 20
            GPIO.setup(STATUS, GPIO.IN)
            #if(STATUS==20):
            if(GPIO.input(STATUS)):
                self.ui.dig_connect_label.setText("Module: Ready!")
                logging.info("Module: Ready! - CellularIoT Shield")
            else:
                self.ui.dig_connect_label.setText("Module: Not ready, check power of module.")
                logging.info("Module: Not ready, check power of module. - CellularIoT Shield")
        elif(text==''):
            QMessageBox.information(self, 'Message', "Please input a Value")
            self.ui.dig_connect_label.setText("Module: Not found.")
            logging.info("Module: Not found.")

    def onDiagnose(self):
        hat_combo = str(self.ui.dig_hat_shield_combobox.currentText())
        hat_label = self.ui.dig_detection_label.text()
        if(hat_combo!="" or hat_label!=""):
            self.ui.textBrowser.setText('')
            sim_message=""
            antenna_message=""
            if(os.path.exists("/dev/ttyUSB2")):
                self.setCursor(Qt.WaitCursor)
                QMessageBox.information(self, 'Message', "Please wait, sending AT commands...")
                port = serial.Serial("/dev/ttyUSB2", baudrate=115200, timeout=1)
                connection=sendATcommand("AT")
                #print(connection)
                if(connection=="OK"):
                    self.ui.textBrowser.append("Connected to the module.")
                    self.ui.textBrowser.append("Sending AT commands...")
                    logging.info("Connected to the module. Sending commands...", exc_info=True)
                    print("Connected to the module.")
                    logging.info("Connected to the module.")
                    print("Sending commands...")
                    logging.info("Sending commands...")
                    
                    time.sleep(0.3)
                    
                    port.write(("AT+CMEE=2"+'\r\n').encode())
                    
                    time.sleep(0.3)
                    ATI = sendATcommand("\nATI")
                    self.ui.textBrowser.append("ATI")
                    self.ui.textBrowser.append(ATI+"\n")
                    time.sleep(0.3)
                    
                    ATV1 = sendATcommand("ATV1")
                    self.ui.textBrowser.append("ATV1")
                    self.ui.textBrowser.append(ATV1+"\n")
                    time.sleep(0.3)
                    
                    ATE1 = sendATcommand("ATE1")
                    self.ui.textBrowser.append("ATE1")
                    self.ui.textBrowser.append(ATE1+"\n")
                    time.sleep(0.3)
                    
                    IPR = sendATcommand("AT+IPR?")
                    self.ui.textBrowser.append("AT+IPR?")
                    self.ui.textBrowser.append(IPR+"\n")
                    
                    COPS = sendATcommand("AT+COPS?")
                    self.ui.textBrowser.append("AT+COPS?")
                    self.ui.textBrowser.append(COPS+"\n")
                    time.sleep(0.3)
                    
                    GSN = sendATcommand("AT+GSN")
                    self.ui.textBrowser.append("AT+GSN")
                    self.ui.textBrowser.append(GSN+"\n")
                    time.sleep(0.3)
                    
                    QURCCFG = sendATcommand("AT+QURCCFG=\"urcport\",\"usbat\"")
                    self.ui.textBrowser.append("AT+QURCCFG=\"urcport\",\"usbat\"")
                    self.ui.textBrowser.append(QURCCFG+"\n")
                    time.sleep(0.3)
                    
                    CPIN = sendATcommand("AT+CPIN?")
                    self.ui.textBrowser.append("AT+CPIN?")
                    self.ui.textBrowser.append(CPIN+"\n")
                    time.sleep(0.3)
                    if(CPIN!="" and CPIN.lower().find('error') > -1):
                        sim_message="SIM card not inserted."
                    else:
                        sim_message="SIM card is inserted."
                    
                    QCCID = sendATcommand("AT+QCCID")
                    self.ui.textBrowser.append("AT+QCCID")
                    self.ui.textBrowser.append(QCCID +"\n")
                    time.sleep(0.3)
                    
                    CREG = sendATcommand("AT+CREG?")
                    self.ui.textBrowser.append("AT+CREG?")
                    self.ui.textBrowser.append(CREG+"\n")
                    time.sleep(0.3)
                    
                    CEREG = sendATcommand("AT+CEREG?")
                    self.ui.textBrowser.append("AT+CEREG?")
                    self.ui.textBrowser.append(CEREG+"\n")
                    time.sleep(0.3)
                    
                    CSQ = sendATcommand("AT+CSQ")
                    self.ui.textBrowser.append("AT+CSQ")
                    self.ui.textBrowser.append(CSQ+"\n")
                    time.sleep(0.3)
                    
                    QCSQ = sendATcommand("AT+QCSQ")
                    self.ui.textBrowser.append("AT+QCSQ")
                    self.ui.textBrowser.append(QCSQ+"\n")
                    time.sleep(0.3)
                    if(CSQ!="" and CSQ.lower().find('99,99') > -1):
                        antenna_message="Not known or not detectable."
                    else:
                        antenna_message="The antenna detected."
                    
                    QNWINFO = sendATcommand("AT+QNWINFO")
                    self.ui.textBrowser.append("AT+QNWINFO")
                    self.ui.textBrowser.append(QNWINFO+"\n")
                    time.sleep(0.3)
                    
                    QSPN = sendATcommand("AT+QSPN")
                    self.ui.textBrowser.append("AT+QSPN")
                    self.ui.textBrowser.append(QSPN+"\n")
                    time.sleep(0.3)
                    
                    CGREG = sendATcommand("AT+CGREG?")
                    self.ui.textBrowser.append("AT+CGREG?")
                    self.ui.textBrowser.append(CGREG+"\n")
                    time.sleep(0.3)
                else:
                    logging.error("AT commands could not be sent.", exc_info=True)
                    logging.error("Serial port connection failed.", exc_info=True)
                    self.ui.textBrowser.append("\nSerial port connection failed.")
                    self.ui.textBrowser.append("AT commands could not be sent.")
                    print("AT commands could not be sent.")
                self.setCursor(Qt.ArrowCursor)
            else:
                self.ui.textBrowser.append("AT commands could not be sent. Make sure your USB is connection.")
                
            
            self.ui.textBrowser.append("\n-- Kernel Sources and Header Files --")
            kernel = os.popen('ls /usr/src').read()
            self.ui.textBrowser.append(kernel)
            
            
            self.ui.textBrowser.append("\n-- System Information --")
            uname = os.popen('uname -a').read()
            self.ui.textBrowser.append(uname)
            
            
            self.ui.textBrowser.append("\n-- USB Cable Status --")
            usb = os.popen('ls /dev/ttyUSB*').read()
            if(usb==""):
                self.ui.textBrowser.append("USB Port Not Recognized")
                self.ui.textBrowser.append("Please, make sure your USB is connection.")
            else:
                self.ui.textBrowser.append(usb)
            
            if(antenna_message!=""):
                self.ui.textBrowser.append("\n-- Antenna Status --")
                self.ui.textBrowser.append(antenna_message)
            
            if(sim_message!=""):
                self.ui.textBrowser.append("\n-- SIM Card Status --")
                self.ui.textBrowser.append(sim_message)

            
            self.ui.textBrowser.append("\n-- QMI & PPP Connection Information --")
            if(os.path.exists("/etc/ppp/peers/provider")):
                self.ui.textBrowser.append("PPP installed.")
            else:
                self.ui.textBrowser.append("PPP is not installed.")
                
            if(os.path.exists("/opt/qmi_files")):
                self.ui.textBrowser.append("QMI installed.")
            else:
                self.ui.textBrowser.append("QMI is not installed.")
            
            self.ui.textBrowser.append("\n-- OS Release --")
            os_release = os.popen('cat /etc/os-release').read()
            self.ui.textBrowser.append(os_release)
            
            self.ui.textBrowser.append("\n-- Raspberry Pi Model Infomation --")
            model = os.popen('cat /proc/device-tree/model').read()
            self.ui.textBrowser.append(model)
        else:
            QMessageBox.information(self, 'Message', "Please input a Value")
        
    
    ##########                 ##########
    #########                   #########
    #######    MAIN FUNCTIONS      ###### 
    ######                          #####
    ####                             #### 

    def onDiagnostic(self):
        self.ui.home.setVisible(False)
        self.ui.installer.setVisible(False)
        self.ui.diagnostic.setVisible(True)
        
    def onInstaller(self):
        self.ui.home.setVisible(False)
        self.ui.installer.setVisible(True)
        self.ui.diagnostic.setVisible(False)
        
    def onMain(self):
        self.setCursor(Qt.ArrowCursor)
        self.ui.home.setVisible(True)
        self.ui.installer.setVisible(False)
        self.ui.diagnostic.setVisible(False)

    ##########                    ##########
    #########                      #########
    #######   INSTALLER  FUNCTIONS    ######
    ######                             #####
    ####                                #### 

    def onSelectservice(self, text):
        logging.info(text)
        label = self.ui.label.text()
        if(text=="QMI"):   
            self.ui.shield_hat_comboBox.clear()
            self.ui.shield_hat_comboBox.addItems(['','Base Shield', 'Base HAT', 'CellularIoT Shield', 'CellularIoT HAT'])
            self.ui.shield_hat_comboBox.activated[str].connect(self.qmi)
            if(label!=""):
                self.ui.qmi_groupBox.setVisible(True)
                self.ui.ppp_groupBox.setVisible(False)
            self.ui.ppp_groupBox.setVisible(False)
        elif (text == "PPP"):   
            self.ui.shield_hat_comboBox.clear() 
            self.ui.shield_hat_comboBox.addItems(['', 'Base Shield', 'CellularIoT Shield','CellularIoT HAT', 'Tracker HAT', 'Base HAT'])
            self.ui.shield_hat_comboBox.activated[str].connect(self.ppp)
            if(label!=""):
                self.ui.qmi_groupBox.setVisible(False)
                self.ui.ppp_groupBox.setVisible(True)
            self.ui.qmi_groupBox.setVisible(False)
        else:
            self.ui.shield_hat_comboBox.clear()
            self.ui.qmi_groupBox.setVisible(False)
            self.ui.ppp_groupBox.setVisible(False)

    def qmi(self,text):
        
        if(text=="Base Shield" or text=="Base HAT" or text=="CellularIoT Shield" or text=="CellularIoT HAT"):
            self.ui.qmi_groupBox.setVisible(True)
            self.ui.ppp_groupBox.setVisible(False)
        elif(text==""):
            self.ui.qmi_groupBox.setVisible(False)

    def ppp(self,text):
        if(text=="Base Shield" or text=="CellularIoT Shield" or text=="CellularIoT HAT" or text=="Base HAT" or text=="Tracker HAT"):
            self.ui.qmi_groupBox.setVisible(False)
            self.ui.ppp_groupBox.setVisible(True)
        elif(text==""):
            self.ui.ppp_groupBox.setVisible(False)

    ##########               ##########
    #########                 #########
    #######   QMI  FUNCTIONS     ######
    ######                        #####
    ####                           ####

    # Reboot system 
    def onReboot(self):
        os.system('sudo reboot')

    def onUpdateButtonClick(self):
        QMessageBox.information(self, 'Info', "Updating, this may take long. Please do not reboot/turn off the power")
        self.calc = External()
        self.calc.countChanged.connect(self.onCountChanged)
        self.calc.start()
        os.system('sudo apt update && sudo apt upgrade -y')
        apn = self.ui.qmi_apn.text()

        with open("/var/lib/sixfab/sixfab-status","w",encoding = "utf-8") as f:
            f.writelines(["1"])

    def onKernelButtonClick(self):
        if(internet_check()):
            self.calc = External()
            self.calc.countChanged.connect(self.onCountChanged2)
            self.calc.start()
            try:
                QMessageBox.information(self, 'Info', "Installing, this may take long. Please do not reboot/turn off the power")
                os.system('sudo apt-get install raspberrypi-kernel-headers' + '> ./setup-and-diagnostic-tool.log 2>&1')
                value = os.popen('ls /usr/src').read()
                version=value[14:20]
                r = requests.get('https://api.github.com/repos/Hexxeh/rpi-firmware/commits')
                r.json()
                a=r.json()
                for x in range(len(a)):
                    message=a[x]['commit']['message']
                    decision = message.find(version)
                    if(decision != -1):
                        print(a[x]['sha'])
                        logging.info("SHA: "+ a[x]['sha'])
                        text="sudo SKIP_WARNING=1 rpi-update " + a[x]['sha']
                        os.system(text + ">> ./setup-and-diagnostic-tool.log 2>&1")
                        logging.info("Install kernel successful.")
                        break
                with open("/var/lib/sixfab/sixfab-status","w",encoding = "utf-8") as f:
                    f.writelines(["2"])
                time.sleep(2)
                os.system('sudo reboot')
            except Exception as e:
                logging.critical(e, exc_info=True)
        else:
            QMessageBox.information(self, 'Message', "No Internet connection")
            print("No Internet connection")
            logging.info("No Internet connection")
        

    def onScriptButtonClick(self):
        if(internet_check()):
            QMessageBox.information(self, 'Info', "Installing, this may take long. Please do not reboot/turn off the power")
            os.system('sudo apt-get install raspberrypi-kernel-headers' + '> ./setup-and-diagnostic-tool.log 2>&1')
            if(os.path.exists("./qmi_install.sh")):
                os.system('rm qmi_install.sh')
                logging.info("Downloading new qmi_install.sh")
                print("Downloading new qmi_install.sh")
            self.calc = External()
            self.calc.countChanged.connect(self.onCountChanged3)
            self.calc.start()
            try:
                os.system('wget https://raw.githubusercontent.com/sixfab/setup-and-diagnostic-tool/master/qmi_install.sh')
                os.system('sudo chmod a+rwx qmi_install.sh')
                os.system('sudo ./qmi_install.sh' + "> ./setup-and-diagnostic-tool.log 2>&1")
            except Exception as e:
                logging.error("QMI install failed.", exc_info=True)
            logging.info("sudo ./qmi_install.sh ... done")
            with open("/var/lib/sixfab/sixfab-status","w",encoding = "utf-8") as f:
                f.writelines(["3"])
            time.sleep(2)
            os.system('sudo reboot')
        else:
            QMessageBox.information(self, 'Message', "No Internet connection")
            print("No Internet connection")
            logging.info("No Internet connection")
        

    def onServiceButtonClick(self):
        apn =self.ui.qmi_apn.text()
        logging.info("QMI APN: "+ apn)
        if(apn==''):
            QMessageBox.information(self, 'Message', "Please input a Value")
        else:
            logging.info("QMI service activation...")
            apn =self.ui.qmi_apn.text()
            label="sudo /opt/qmi_files/quectel-CM/quectel-CM -s " + apn + "&"
            try:
                if(os.path.exists("/opt/qmi_files/quectel-CM")):
                    os.system(label + ">> ./setup-and-diagnostic-tool.log 2>&1")
                    self.ui.qmi_status_label.setText("QMI service: Active")
                    self.ui.qmi_status_label.setVisible(True)
                else:
                    self.ui.qmi_status_label.setText("QMI service could not be activated.")
                    self.ui.qmi_status_label.setVisible(True)
            except Exception as e:
                logging.error("os.system(" + label + ") failed.", exc_info=True)


    def onTestButtonClick(self):
        ifconfig = os.popen('ifconfig').readlines()
        wwanControl=True
        for i in range(len(ifconfig)):
            interface=ifconfig[i]
            wwanControl=interface.find("wwan0")
            if(wwanControl != -1):
                message=sendPing("qmi")
                self.ui.qmi_test_label.setVisible(True)
                self.ui.qmi_test_label.setText(message)
                print(message)
                logging.info("QMI Test button message: "+message)
                wwanControl=True
                break
            else:
                wwanControl=False

        if(wwanControl==False):
            logging.info("QMI interface not found.") 
            self.ui.qmi_test_label.setText("QMI interface not found.") # "Make sure USB cable is connected.
    
    def onAutoButtonClick(self):
        apn2 =self.ui.qmi_apn.text()
        if(apn2==''):
            QMessageBox.information(self, 'Message', "Please input a APN")
        else:
            if(internet_check()):
                if(os.path.exists("./install_auto_connect.sh")):
                    os.system("rm install_auto_connect.sh")
                    print("Downloading new install_auto_connect.sh")
                    logging.info("Downloading new install_auto_connect.sh")
                try:
                    os.system('wget https://raw.githubusercontent.com/sixfab/setup-and-diagnostic-tool/master/install_auto_connect.sh')
                    os.system('sudo chmod a+rwx install_auto_connect.sh')
                except Exception as e:
                    logging.error("Auto connect download failed.", exc_info=True)
                with open("./install_auto_connect.sh","r+",encoding = "utf-8") as f:
                    data = f.readlines()
                    data.insert(2, "carrierapn=\""+apn2+"\"\n")
                    f.seek(0)
                    f.writelines(data)
                try:
                    os.system("sudo ./install_auto_connect.sh" + ">> ./setup-and-diagnostic-tool.log 2>&1")
                    active = os.popen("systemctl is-active qmi_reconnect.service").read()
                    self.ui.qmi_auto_label.setVisible(True)
                    self.ui.qmi_auto_label.setText("QMI reconnect Service: "+active)
                    logging.info("QMI Reconnect Service: " + active)
                except Exception as e:
                    logging.critical(e, exc_info=True)
            else:
                QMessageBox.information(self, 'Message', "No Internet connection")
                print("No Internet connection")
                logging.info("No Internet connection")

    def state_changed(self):
        if self.ui.qmi_autoConnect_check.isChecked():
            #self.ui.qmi_apn_auto.setVisible(True)
            self.ui.autoButton.setVisible(True)
            #self.ui.apn_label_2.setVisible(True)
        else:
            #self.ui.qmi_apn_auto.setVisible(False)
            self.ui.autoButton.setVisible(False)
            #self.ui.apn_label_2.setVisible(False)
            self.ui.qmi_auto_label.setVisible(False)

    def onCountChanged(self, value):
        self.ui.progressBar.setValue(value)

    def onCountChanged2(self, value):
        self.ui.progressBar_2.setValue(value)

    def onCountChanged3(self, value):
        self.ui.progressBar_3.setValue(value)

    ##########               ##########
    #########                 #########
    #######   PPP  FUNCTIONS     ######
    ######                        #####
    ####                           ####

    def onPPPInstallButton(self):
        #'Base Shield', 'CellularIoT Shield','CellularIoT HAT', 'Tracker HAT', 'Base HAT'
        if(os.path.exists("/proc/device-tree/hat")):
            f=open("/proc/device-tree/hat/product_id", "r")
            product_id = f.read().splitlines()
            product_id = product_id[0].rsplit('\x00')
            logging.info("Produc ID: " + product_id[0])
            f.close()
        else:
            print("/proc/device-tree/hat not found. If you have not connected your HAT to Raspberry Pi, connect and reboot.")
            logging.info("/proc/device-tree/hat not found.")
        apn3 =self.ui.ppp_apn.text()
        port = str(self.ui.ppp_port_comboBox.currentText())
        autoConnect = str(self.ui.ppp_auto_comboBox.currentText())
        shield=str(self.ui.shield_hat_comboBox.currentText())
        try:
            if(shield==""):
                if(product_id[0] == '0x0003'):
                    shield = "Base HAT"
                elif(product_id[0] == '0x0001' or product_id[0] == '0x0005'):
                    shield = "CellularIoT HAT"
                elif(product_id[0] == '0x0004'):
                    shield = "Tracker HAT"
                else:
                    shield = "Base HAT"
        except Exception as e:
            logging.critical(e, exc_info=True)
        if(apn3=="" or port=="" or autoConnect==""):
            QMessageBox.information(self, 'Message', "Please input a Value")
        else:
            logging.info("Shield/HAT: "+ shield)
            logging.info("APN: "+ apn3)
            logging.info("Port: "+ port)
            logging.info("AutoConnect: "+ autoConnect)
            print(shield)
            print(apn3)
            print(port)
            print(autoConnect)
            hat=assignment(shield) 
            if(internet_check()):
                if(os.path.exists("./ppp_install.sh")):
                    os.system('rm ppp_install.sh')
                    print("Downloading new ppp_install.sh")
                    logging.info("Downloading new ppp_install.sh")
                try:
                    os.system('wget https://raw.githubusercontent.com/sixfab/setup-and-diagnostic-tool/master/ppp_install.sh')
                    os.system('sudo chmod +x ppp_install.sh')
                    install='sudo ./ppp_install.sh '+ hat +' '+ apn3 + ' '+ ' '+port + ' ' +autoConnect
                    print(install)
                except Exception as e:
                    logging.error("PPP Download failed.", exc_info=True)
                    logging.info("PPP install command: " + install)
                #QMessageBox.information(self, 'Info', "Installing, this may take long. Please do not reboot/turn off the power")
                try:
                    os.system(install + ">> ./setup-and-diagnostic-tool.log 2>&1")
                except Exception as e:
                    logging.error("PPP install failed.", exc_info=True)
            else:
                QMessageBox.information(self, 'Message', "No Internet connection")
                print("No Internet connection")
                logging.info("No Internet connection")
                

    def onAddCredentialButton(self):
        user =self.ui.username.text()  
        password =self.ui.password.text()
        logging.info("Credential Username and Password:"+ user +" - " + password)
        if(os.path.exists("/etc/ppp/peers/provider")):
            print("Provider file found.")
            os.system("sudo chmod a+rwx /etc/ppp/peers/provider")
            with open("/etc/ppp/peers/provider","w",encoding = "utf-8") as f:
                logging.info("Provider file found.")
                user_new ="user \""+ user +"\"\n"
                password_new ="password \""+password+"\""
                f.writelines(user_new)
                f.writelines(password_new)
            QMessageBox.information(self, 'Message', "Added")
        else:
            self.ui.textBrowser.append("PPP is not installed.")
            logging.info("Add credential - PPP is not installed.")
        self.ui.username.setText("")
        self.ui.password.setText("")

    def onPPPTestButton(self):
        self.ui.ppp_test_label.setVisible(True)
        try:
            os.system("sudo pon" + ">> ./setup-and-diagnostic-tool.log 2>&1")
        except Exception as e:
            logging.error("sudo pon : failed.", exc_info=True)
            print("sudo pon : failed")
        ifconfig = os.popen('ifconfig').readlines()
        pppControl=True
        for i in range(len(ifconfig)):
            interface=ifconfig[i]
            pppControl=interface.find("ppp0")
            if(pppControl != -1):
                message=sendPing("ppp")
                self.ui.ppp_test_label.setVisible(True)
                self.ui.ppp_test_label.setText(message)
                logging.info("PPP Test Message: "+ message)
                print(message)
                pppControl=True
                break
            else:
                pppControl=False

        if(pppControl==False):
            self.ui.ppp_test_label.setText("Interface not found.") # Make sure USB cable is connected.
            logging.info("Interface not found.")

    def password_changed(self):
        if self.ui.show_checkBox.isChecked():
            self.ui.password.setEchoMode(QLineEdit.Normal)
        else:
            self.ui.password.setEchoMode(QLineEdit.Password)
            self.ui.show_checkBox.setText("Show")

    def credential_changed(self):
        if self.ui.credential_checkBox.isChecked():
            self.ui.credential_frame.setVisible(True)
            self.ui.autoConnect_label.setGeometry(100, 235, 381, 31) # QWidget.setGeometry (self, int ax, int ay, int aw, int ah)
            self.ui.ppp_auto_comboBox.setGeometry(440, 235, 121, 31)
            self.ui.label_31.setGeometry(70, 230, 41, 41)

            self.ui.label_32.setGeometry(70, 320, 21, 41)
            self.ui.pppInstallButton.setGeometry(260,280,186,31)
            self.ui.pppTestButton.setGeometry(150,325,186,31)
            self.ui.ppp_test_label.setGeometry(360,325,211,41)
        else:
            self.ui.credential_frame.setVisible(False)
            self.ui.autoConnect_label.setGeometry(100, 155, 381, 31)
            self.ui.ppp_auto_comboBox.setGeometry(440, 154, 121, 31)
            self.ui.label_31.setGeometry(70, 150, 21, 41)
            self.ui.label_32.setGeometry(70, 245, 21, 41)


            self.ui.pppInstallButton.setGeometry(240,200,186,31)
            self.ui.pppTestButton.setGeometry(130,250,186,31)
            self.ui.ppp_test_label.setGeometry(330,255,211,41)


class External(QThread):
    countChanged = pyqtSignal(int)
    def run(self):
        count = 0
        while count < TIME_LIMIT:
            count +=1
            self.countChanged.emit(count)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DesktopTool()
    window.show()
    sys.exit(app.exec_())