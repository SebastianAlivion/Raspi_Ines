#!/bin/bash
echo -e "\e[93mPrograms"
cd ..
cp -R Programs/meoh_prototype/data /home/pi
mv data data_old
mv Programs Programs_old


git clone https://github.com/SebastianAlivion/Raspi_Ines
chown -R pi:pi RaspberryPiSetup
cd RaspberryPiSetup
mv Programs /home/pi
cd ..
rm -R RaspberryPiSetup

cp -R data_old/ Programs/meoh_prototype/data
rm -R data_old/
rm -R Programs_old/
chown -R pi:pi Programs
