import subprocess
import piwifi

def connect_to_wifi(ssid, password):
    try:
        # Check if the SSID is known in the wpa_supplicant.conf file
        known_ssid = check_known_ssid(ssid)
        current_ssid = get_current_ssid()

        if known_ssid:
            print(f"SSID '{ssid}' is already known.")
        else:
            # Append the new network configuration to wpa_supplicant.conf
            append_new_network(ssid, password)

            # Restart the wpa_supplicant service to apply changes
            restart_wpa_supplicant()

        # Use wpa_cli to connect to the new or known SSID
        subprocess.run(["wpa_cli", "-i", "wlan0", "select_network", ssid])

        print(f"Connected to SSID: {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Failed to connect to the network.")

def check_known_ssid(ssid):
    # Check if the SSID is known in wpa_supplicant.conf
    # You can implement this function to read and search the configuration file
    import piwifi

def get_current_ssid():
    wifi = piwifi.WiFi()
    interfaces = wifi.interfaces()

    # Assuming you're using the first available interface
    if interfaces:
        first_interface = interfaces[0]
        current_ssid = first_interface.current_ssid
        return current_ssid
    else:
        return None

# Get the current SSID
#current_ssid = get_current_ssid()

#if current_ssid:
#    print(f"Connected to SSID: {current_ssid}")
#else:
#    print("Not connected to any Wi-Fi network.")
#

def append_new_network(ssid, password):
    # Append a new network configuration to wpa_supplicant.conf
    # You can implement this function to add the network configuration
    pass

def restart_wpa_supplicant():
    # Restart the wpa_supplicant service using systemctl
    subprocess.run(["sudo", "systemctl", "restart", "wpa_supplicant"])

# Example usage:
desired_ssid = "Mounda"
desired_password = "moundasummer"
connect_to_wifi(desired_ssid, desired_password)
