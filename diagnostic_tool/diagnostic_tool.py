# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os
import sys
import logging
import time
import serial
from pprint import pprint
from yaspin import yaspin
from tqdm import trange
from tqdm import tqdm
from PyInquirer import style_from_dict, Token, prompt, Separator
from examples import custom_style_2


logging.basicConfig(filename='diagnostic-tool.log', format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s: - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

main_questions = [
            '1. Sending AT commands',
            '2. Kernel Sources and Header Files',
            '3. System Information',
            '4. USB Port',
            '5. QMI & PPP Setup Information',
            '6. OS Release',
            '7. Raspberry Pi Model Infomation',
            '8. Exit'
            ]
choice_question = [
        '1. Home',
        '2. Exit',
    
]
#os.system("")
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

#for i in trange(10):
    #   sleep(10)

#
#
#   FUNCTIONS
#
#
#
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
    


def send_command():
    if(os.path.exists("/dev/ttyUSB2")):
        port = serial.Serial("/dev/ttyUSB2", baudrate=115200, timeout=1)
        connection=sendATcommand("AT")
        if(connection=="OK"):
            
            logging.info("Connected to the module. Sending commands...")
            with yaspin(text="Sending AT Commands...", color="yellow") as sp:
                
                
                time.sleep(0.5)
                sp.write(style.GREEN + "Connected to the module.")
                logging.info("Connected to the module.")
                logging.info("Sending commands...")
                time.sleep(0.5)
                
                port.write(("AT+CMEE=2"+'\r\n').encode())
                ATI = sendATcommand("ATI")
                sp.write(style.YELLOW + "\n" + ATI + "\n")
                time.sleep(0.5)
                
                ATV1 = sendATcommand("ATV1")
                sp.write(style.YELLOW + "ATV1:"+ ATV1 + "\n")
                time.sleep(0.5)
                
                ATE1 = sendATcommand("ATE1")
                sp.write(style.YELLOW + "ATE1:"+ ATE1 + "\n")
                time.sleep(0.5)
                
                IPR = sendATcommand("AT+IPR?")
                sp.write(style.YELLOW + "AT+IPR?:"+ IPR + "\n")
                time.sleep(0.5)
                
                COPS = sendATcommand("AT+COPS?")
                sp.write(style.YELLOW + "AT+COPS?:"+ COPS + "\n")
                time.sleep(0.5)
                
                GSN = sendATcommand("AT+GSN")
                sp.write(style.YELLOW + "AT+GSN:" + GSN +"\n")
                time.sleep(0.5)
                
                QURCCFG = sendATcommand("AT+QURCCFG=\"urcport\",\"usbat\"")
                sp.write(style.YELLOW + "AT+QURCCFG=\"urcport\",\"usbat\":"+ QURCCFG +"\n")
                time.sleep(0.5)
                
                CPIN = sendATcommand("AT+CPIN?")
                sp.write(style.YELLOW + "AT+CPIN?:" + CPIN+"\n")
                time.sleep(0.5)
                
                CREG = sendATcommand("AT+CREG?")
                sp.write(style.YELLOW + "AT+CREG?:" + CREG+"\n")
                time.sleep(0.5)
                
                CEREG = sendATcommand("AT+CEREG?")
                sp.write(style.YELLOW + "AT+CEREG?:" + CEREG+"\n")
                time.sleep(0.5)
                
                CSQ = sendATcommand("AT+CSQ")
                sp.write(style.YELLOW + "AT+CSQ:" + CSQ+"\n")
                time.sleep(0.5)
                
                QCSQ = sendATcommand("AT+QCSQ")
                sp.write(style.YELLOW + "AT+QCSQ:" + QCSQ+"\n")
                time.sleep(0.5)
                
                QNWINFO = sendATcommand("AT+QNWINFO")
                sp.write(style.YELLOW + "AT+QNWINFO:" + QNWINFO+"\n")
                time.sleep(0.5)
                
                QSPN = sendATcommand("AT+QSPN")
                sp.write(style.YELLOW + "AT+QSPN:" + QSPN + "\n")
                time.sleep(0.5)
                
                CGREG = sendATcommand("AT+CGREG?")
                sp.write(style.YELLOW + "AT+CGREG?:" + CGREG+"\n")
                time.sleep(0.5)
                
                sp.ok("✔")
        else:
            with yaspin(text="Sending AT Commands...", color="red") as sp:
                time.sleep(1)
                sp.write(style.RED + "AT commands could not be sent.")
                logging.error("AT commands could not be sent.", exc_info=True)
                sp.fail("x")
    else:
        with yaspin(text="Sending AT Commands...", color="red") as sp:
                time.sleep(1)
                sp.write(style.RED + "AT commands could not be sent. Make sure your USB is connection.")
                logging.error("AT commands could not be sent. Make sure your USB is connection.", exc_info=True)
                sp.fail("x")

def switch(value):
    while(True):
        questions2 = [{
                'type': 'list',
                'name': 'choice',
                'message': 'Menu',
                'choices': [
                    '1. Home',
                    '2. Exit',
                ]
            }]
        if(value == main_questions[0]):
            for i in tqdm(range(9),desc="Sending"):
                time.sleep(0.2)
            with yaspin(color="yellow") as sp:
                time.sleep(1)
                send_command()
            answers = prompt(questions2, style=custom_style_2)
            if(answers['choice']== choice_question[0]):
                break
            else:
                sys.exit()
        elif(value == main_questions[1]):
            print(style.MAGENTA + "\n--- Kernel Sources and Header Files ---")
            kernel = os.popen('ls /usr/src').read()
            print((style.YELLOW + kernel))

            answers = prompt(questions2, style=custom_style_2)
            if(answers['choice']== choice_question[0]):
                break
            else:
                sys.exit()
        elif(value == main_questions[2]):
            print(style.MAGENTA + "\n--- System Information ---")
            uname = os.popen('uname -a').read()
            print(style.YELLOW + uname)

            answers = prompt(questions2, style=custom_style_2)
            if(answers['choice']== choice_question[0]):
                break
            else:
                sys.exit()
        elif(value == main_questions[3]):
            print(style.MAGENTA + "\n--- USB Port ---")
            usb = os.popen('ls /dev/ttyUSB*').read()
            if(usb==""):
                print(style.RED + "USB Port Not Recognized")
                print(style.RED + "Please, make sure your USB is connection.")
            else:
                print(style.YELLOW + usb)

            answers = prompt(questions2, style=custom_style_2)
            if(answers['choice']== choice_question[0]):
                break
            else:
                sys.exit()
        elif(value == main_questions[4]):
            print(style.MAGENTA + "\n--- QMI & PPP Connection Information ---")
            if(os.path.exists("/etc/ppp/peers/provider")):
                print(style.YELLOW + "PPP installed.")
            else:
                print(style.RED + "PPP is not installed.")
            if(os.path.exists("/opt/qmi_files")):
                print(style.YELLOW + "QMI installed.")
            else:
                print(style.RED + "QMI is not installed.")

            answers = prompt(questions2, style=custom_style_2)
            if(answers['choice']== choice_question[0]):
                break
            else:
                sys.exit()
        elif(value == main_questions[5]):
            print(style.MAGENTA + "\n--- OS Release ---")
            os_release = os.popen('cat /etc/os-release').read()
            print(style.YELLOW + os_release)

            answers = prompt(questions2, style=custom_style_2)
            if(answers['choice']== choice_question[0]):
                break
            else:
                sys.exit()
        elif(value == main_questions[6]):
            print(style.MAGENTA + "\n--- Raspberry Pi Model Infomation ---")
            model = os.popen('cat /proc/device-tree/model').read()
            print(style.YELLOW + model)

            answers = prompt(questions2, style=custom_style_2)
            if(answers['choice']== choice_question[0]):
                break
            else:
                sys.exit()
        elif(value == main_questions[7]):
            sys.exit()
    

def main():
    print(r"""
  ____  _       __       _      
 / ___|(_)_  __/ _| __ _| |__   
 \___ \| \ \/ / |_ / _` | '_ \  
  ___) | |>  <|  _| (_| | |_) | 
 |____/|_/_/\_\_|  \__,_|_.__/  
            """)
    
    print(r"""
  ____  _                             _   _        _____           _ 
 |  _ \(_) __ _  __ _ _ __   ___  ___| |_(_) ___  |_   _|__   ___ | |
 | | | | |/ _` |/ _` | '_ \ / _ \/ __| __| |/ __|   | |/ _ \ / _ \| |
 | |_| | | (_| | (_| | | | | (_) \__ \ |_| | (__    | | (_) | (_) | |
 |____/|_|\__,_|\__, |_| |_|\___/|___/\__|_|\___|   |_|\___/ \___/|_|
                |___/                                                
            """)
    while(True):
        try:
            questions = [{
            'type': 'list',
            'name': 'main',
            'message': 'What do you want to do?',
            'choices': main_questions
        }]
        
            answers = prompt(questions, style=custom_style_2)
            switch(answers['main'])
        except ValueError:
            print("####")
            continue

if __name__ == '__main__':
    #answer = prompt('Give me some input: ')
    #print('You said: %s' % answer)
    main()
    