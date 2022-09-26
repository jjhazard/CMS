#!/bin/bash

if [[ $# -ne 2 ]];
then
 echo "Setup requires exactly two arguments."
 exit 0
fi
if [[ "$1" != "CRS" ]] && [[ "$1" != "CVS" ]];
then
 echo "First argument must be either 'CRS' or 'CVS'."
 exit 0
fi
if ! [[ $2 =~ [1-6] ]];
then
 echo "Second argument must be a number from 1-6:"
 echo "1 = Eastern Time Zone (EDT)"
 echo "2 = Central Time Zone (CDT)"
 echo "3 = Mountain Time Zone (MDT)"
 echo "4 = Pacific Time Zone (PDT)"
 echo "5 = Alaska Time Zone (AKDT)"
 echo "6 = Hawaii-Aleutian Time Zone (HST)"
 exit 0
fi

#Update system and install latest python
sudo apt-get update
sudo apt-get install python3

#Install program dependencies
sudo python3 -m pip install pyserial
sudo python3 -m pip install Adafruit-Blinka
sudo python3 -m pip install apscheduler
sudo python3 -m pip install adafruit-circuitpython-matrixkeypad
sudo python3 -m pip install adafruit-circuitpython-rfm9x

#Install CMS from repository
wget https://github.com/jjhazard/CMS/archive/master.zip
unzip master.zip
rm master.zip
cd CMS-main/CMS

#Write bash script to run program if it crashes
echo "#!/bin/bash

cd /home/pi/CMS-main/CMS
python3 $1.py &
PID=\$!
while true
do
 wait \${PID}
 python3 $1.py &
 PID=\$!;
done;" > CMSrun.sh

#Make bash script executable and set it to run on startup
ORIGINAL='exit 0'
NEW='bash \/home\/CMS-main\/CMS\/CMSrun.sh \&\n\nexit 0'
sudo sed -i -E "$ s/$ORIGINAL/$NEW/" /etc/rc.local

#Set local timezone to match product end location
case $2 in
 1)
  sudo timedatectl set-timezone America/New_York
  ;;
 2)
  sudo timedatectl set-timezone America/Chicago
  ;;
 3)
  sudo timedatectl set-timezone America/Denver
  ;;
 4)
  sudo timedatectl set-timezone America/Los_Angeles
  ;;
 5}
  sudo timedatectl set-timezone America/Anchorage
  ;;
 6}
  sudo timedatectl set-timezone America/Adak
  ;;
esac

sudo reboot
