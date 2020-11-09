#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   	echo "This script must be run as root" 
   	exit 1
else
    #Update and Upgrade
    echo "0. Updating and Upgrading"
    sudo apt update && sudo apt upgrade -y

    echo"1. Installing the access point and network management software"

    echo "1.1 Installing hostapd"
    sudo apt install hostapd -y

    echo "Enable the wireless access point service and set it to start when your Raspberry Pi boots"
    sudo systemctl unmask hostapd
    sudo systemctl enable hostapd

    echo "1.2 Installing dnsmasq"
    sudo apt install dnsmasq -y

    echo "1.3 Installing netfilter-persistent and its plugin iptables-persistent"
    # This utility helps by saving firewall rules and restoring them when the Raspberry Pi boots
    sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent

    echo "2. Setting up the network router"
    echo "Configuring the static IP address in dhcpcd configuration file"
    sudo cp ${PWD}/dhcpcd.conf.custom /etc/dhcpcd.conf

    echo "2.1 Configure the DHCP and DNS services for the wireless network"
    sudo cp ${PWD}/dnsmasq.conf.custom /etc/dnsmasq.conf

    echo "3. Configure the access point software"
    sudo cp ${PWD}/hostapd.conf /etc/hostapd/hostapd.conf

    echo "4. Done!!!"
    echo "Rebooting in 10 seconds"
    sleep 10
    sudo systemctl reboot











