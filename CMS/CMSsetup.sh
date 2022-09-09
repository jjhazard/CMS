#!/bin/bash

#Update system and install latest python
sudo apt-get update
sudo apt-get install python3

#Install program dependencies
sudo python3 -m pip install pyserial
sudo python3 -m pip install Adafruit-Blinka
sudo python3 -m pip install apscheduler
sudo python3 -m pip install adafruit-circuitpython-matrixkeypad
sudo python3 -m pip install adafruit-circuitpython-rfm9x

#Install git and clone CMS from repository
wget https://github.com/jjhazard/CMS/archive/master.zip
unzip master.zip
cd CMS-main
cd CRM
ls .

#Set local timezone to match product end location
sudo timedatectl set-timezone $1

