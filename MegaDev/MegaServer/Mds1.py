import comtypes
import pywifi
import time

def find_interface_by_name(interface_name):
    wifi = pywifi.PyWiFi()

    # Get a list of available Wi-Fi interfaces
    interfaces = wifi.interfaces()

    # Find the desired interface by name
    for interface in interfaces:
        if interface.name() == interface_name:
            return interface

    return None

def get_current_ssid(interface_name):
    # Find the Wi-Fi interface by name
    interface = find_interface_by_name(interface_name)

    if interface:
        if interface.status() == pywifi.const.IFACE_CONNECTED:
            return interface.ssid()
    return None

# linux
# Specify the interface name (e.g., wlan1)
interface_name = "wlan1"

# Get the current SSID for wlan1
current_ssid = get_current_ssid(interface_name)

# windows
#wifi = pywifi.PyWiFi()
#iface = wifi.interfaces()[0] # first WiFi interface
#iface.scan() 
time.sleep(0.3)
#results = iface.scan_results()
#if not results:
#    print("No Wifi networks found!")
#else:
#    for i in results:
#        bssid = i.bssid
#        ssid = i.ssid
#        print (f"{bssid}: {ssid}")


#    print(f"Connected to SSID on {bssid}: {ssid}")
