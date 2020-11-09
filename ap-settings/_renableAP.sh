#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   	echo "This script must be run as root" 
   	exit 1
else
    echo "Restoring dhcpcd.conf.custom"
    sudo cp ${PWD}/dhcpcd.conf.custom /etc/dhcpcd.conf

    echo "Enabling hostapd and dnsmasq"
    sudo systemctl enable hostapd dnsmasq

    echo "Done... rebooting in 3 seconds!!!"

    sudo reboot 0
    