#!/bin/sh

YELLOW='\033[1;33m'
RED='\033[0;31m'
SET='\033[0m'

OLD_DIR="/home/pi/files"
DIR="/opt/qmi_files"
service_name=qmi_reconnect
status="$(systemctl is-active $service_name.service)"
if [ "$status"="active" ]; then
    systemctl stop $service_name.service
    systemctl disable $service_name.service
fi

echo "${YELLOW}Clear Old Files${SET}"
if [ -d "$OLD_DIR/quectel-CM/" ]; then
    rm -rf $OLD_DIR
fi
if [ -d "$DIR" ]; then
    rm -rf $DIR
fi

echo "${YELLOW}Change directory to /home/pi${SET}"
cd /home/pi

echo "${YELLOW}Downloading source files${SET}"
wget https://github.com/sixfab/Sixfab_RPi_3G-4G-LTE_Base_Shield/raw/master/tutorials/QMI_tutorial/src/quectel-CM.zip
unzip quectel-CM.zip -d $DIR && rm -r quectel-CM.zip


#echo "${YELLOW}Updating rpi${SET}"
#apt update

#echo "${YELLOW}Downlading kernel headers${SET}"
#apt install raspberrypi-kernel-headers
echo "${YELLOW}Checking Kernel${SET}"

case $(uname -r) in
    4.14*) echo $(uname -r) based kernel found
        echo "${YELLOW}Downloading source files${SET}"
        wget https://github.com/sixfab/Sixfab_RPi_3G-4G-LTE_Base_Shield/raw/master/tutorials/QMI_tutorial/src/4.14.zip -O drivers.zip
        unzip drivers.zip -d $DIR && rm -r drivers.zip;;
    4.19*) echo $(uname -r) based kernel found 
        echo "${YELLOW}Downloading source files${SET}"
        wget https://github.com/sixfab/Sixfab_RPi_3G-4G-LTE_Base_Shield/raw/master/tutorials/QMI_tutorial/src/4.19.1.zip -O drivers.zip
        unzip drivers.zip -d $DIR && rm -r drivers.zip;;
    *) echo "Driver for $(uname -r) kernel not found";exit 1;

esac

echo "${YELLOW}Installing udhcpc${SET}"
apt install udhcpc

echo "${YELLOW}Copying udhcpc default script${SET}"
mkdir -p /usr/share/udhcpc
cp $DIR/quectel-CM/default.script /usr/share/udhcpc/
chmod +x /usr/share/udhcpc/default.script

echo "${YELLOW}Change directory to /home/pi/files/drivers${SET}"
cd $DIR/drivers
make && make install

echo "${YELLOW}Change directory to /home/pi/files/quectel-CM${SET}"
cd $DIR/quectel-CM
make
