import piwifi

def get_current_ssid(interface_name):
    wifi = piwifi.WiFi()
    interface = wifi.interface(interface_name)

    if interface:
        current_ssid = interface.current_ssid
        return current_ssid
    else:
        return None

# Specify the interface name (e.g., wlan1)
interface_name = "wlan1"

# Get the current SSID for wlan1
current_ssid = get_current_ssid(interface_name)

if current_ssid:
    print(f"Connected to SSID on {interface_name}: {current_ssid}")
else:
    print(f"Not connected to any Wi-Fi network on {interface_name}.")
