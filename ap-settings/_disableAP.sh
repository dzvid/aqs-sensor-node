#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   	echo "This script must be run as root" 
   	exit 1
else
    echo "Setting wpa_supplicant with your wifi settings"
    sudo cp ${PWD}/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

    echo "Restoring dhcpcd.conf.orig"
    sudo cp ${PWD}/dhcpcd.conf.orig /etc/dhcpcd.conf

    echo "Disabling hostapd and dnsmasq"
    sudo systemctl disable hostapd dnsmasq

    echo "Done... rebooting in 3 seconds!!!"

    sudo reboot 0
    