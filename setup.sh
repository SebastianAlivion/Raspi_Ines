#!/bin/bash
echo -e "\e[93mWelcome!"
echo -e "\e[96mUpdate"
apt-get -y update

echo -e "\e[95mUpgrade"
apt-get -y upgrade

echo -e "\e[96mSetuptools"
pip3 install -- upgrade setuptools

echo -e "\e[95mPython Shell"
cd ~
pip3 install --upgrade adafruit-python-shell

echo -e "\e[96mBlinka Script"
wget https://raw.githubusercontent.com/SebastianAlivion/Raspi_Ines/main/blinka.py
python3 blinka.py

echo -e "\e[95mMatplotlib"
apt-get -y install python3-matplotlib

echo -e "\e[96mPiGPIO"
rm pigpio.zip
rm -rf PIGPIO
wget https://github.com/joan2937/pigpio/archive/refs/tags/V71.zip
unzip V71.zip
cd pigpio-71
make 
make install

echo -e "\e[95mMPRLS"
pip3 install adafruit-circuitpython-mprls

echo -e "\e[96mSGP30"
pip3 install adafruit-circuitpython-sgp30

echo -e "\e[95mPID"
pip3 install simple-pid==0.2.4

echo -e "\e[96mGUI"
pip3 install pysimplegui

echo -e "\e[95mPrograms"
git clone https://github.com/SebastianAlivion/Raspi_Ines
chown -R pi:pi RaspberryPiSetup
cd RaspberryPiSetup
mv Programs /home/pi
cd ..
rm -r RaspberryPiSetup

echo -e "\e[93mDo you want to reboot?"
read pie
if [[ $pie == y* ]]; then
    reboot
else
    echo "Prior to first use, please reboot!"
fi
