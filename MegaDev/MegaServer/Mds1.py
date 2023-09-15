import pywifi

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


# Specify the interface name (e.g., wlan1)
interface_name = "wlan1"

# Get the current SSID for wlan1
current_ssid = get_current_ssid(interface_name)

if current_ssid:
    print(f"Connected to SSID on {interface_name}: {current_ssid}")
else:
    print(f"Not connected to any Wi-Fi network on {interface_name}.")
