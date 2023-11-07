# Control server - takes commands from a kviy app running on a remote
# device, it then acts on those commands to 1) show SSIDs available 2) update
# the wpa_supplicant.conf and 3) other things like reboot
#
import paho.mqtt.client as mqtt
import subprocess
import re
from WifiNetwork import WifiNetwork
import pywifi
import logging
import json

# variables - MQTT broker details
broker_address = "localhost"
broker_port = 1883
topic = "Command"

# inteface variable
interface_index = 0

# path git pto wpa_supplicant.conf file
wpa_supplicant_file = "/etc/wpa_supplicant/wpa_supplicant.conf"

# functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    print("Received message: " + message)
    command, data = message.split(",")
    process_command (command, data)

def process_command (command, data):
    if command == "test":
        print("test")
    elif command=="GET-AVAILABLE":
        # List available Wi-Fi profiles
        available_profiles = list_available_profiles(interface_index) # 0 for wlan0

        # Serialize the list of profiles to JSON
        serialized_profiles = json.dumps(available_profiles)

        #ssids = list_available_ssids("wlan0")  # Replace with the index of the desired interface
        #client.publish("Response", ",".join(ssids))
        #client.publish("Response", "Megadish,Mounda")
        client.publish("Response", serialized_profiles)
        #print ("published to Response " + ",".join(ssids))
    elif command=="GET-STORED":
        # List stored Wi-Fi profiles
        stored_profiles = list_stored_profiles(interface_index)

        # Serialize the list of profiles to JSON
        serialized_profiles = json.dumps(stored_profiles)

        client.publish("Response", serialized_profiles)
        #ssids = list_stored_ssids()
        #client.publish("Response", ",".join(ssids))
    else:
        print ("Command not recognised:" + command)

# command functions
def list_available_ssids(interface):
    command = f"sudo iwlist {interface} scan | grep ESSID"
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    ssids = [line.split(":")[1].strip().strip('"') for line in output.split("\n") if "ESSID:" in line]
    return ssids        

def list_available_ssids2(interface):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[interface]
    iface.scan()
    ssids = [network.ssid for network in iface.scan_results() if network.ssid]
    return ssids

def list_available_profiles(interface_index):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[interface_index]
    
    # Perform a scan to retrieve available network information
    iface.scan()
    
    # Retrieve and return available network profiles
    available_profiles = list(iface.scan_results())
    
    return available_profiles

def list_stored_profiles(interface_index):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[interface_index]
    
    # Retrieve and return stored network profiles
    stored_profiles = list(iface.network_profiles())
    
    return stored_profiles

def list_stored_ssids():
    wifi_networks = load_wifi_networks(wpa_supplicant_file)
    # loop round the networks and convert to an array of ssids
    for ssid, network in wifi_networks.items():
        print(f"SSID: {ssid}")
        print(f"Priority: {network.priority}")
        ssids = ssid
    return ssids 

def update_wpa_supplicant(ssid, password):
    # Open the wpa_supplicant.conf file in append mode
    with open(wpa_supplicant_file, "a") as file:
        file.write(f'\nnetwork={{\n\tssid="{ssid}"\n\tpsk="{password}"\n}}\n')
        print("Wi-Fi network configuration added to wpa_supplicant.conf")

# helper functions
#
def load_wifi_networks(file_path):
    networks = {}
    with open(file_path, "r") as file:
        config_data = file.read()

    # Define a list of attribute tokens to search for
    attribute_tokens = ["ssid", "psk", "security_type", "priority"]

    # Initialize variables to store attribute values
    current_network = {}
    
    for line in config_data.split("\n"):
        # Check if the line contains an attribute token
        for token in attribute_tokens:
            token_pattern = f'{token}="([^"]*)"'
            match = re.search(token_pattern, line)
            if match:
                current_network[token] = match.group(1)
                break
        
        # If the line is the end of a network block, create a WifiNetwork object
        if line.strip() == "}":
            if "ssid" in current_network:
                network = WifiNetwork(
                    current_network["ssid"],
                    current_network.get("psk", ""),
                    current_network.get("security_type", ""),
                    priority=int(current_network.get("priority", 0))
                )
                networks[current_network["ssid"]] = network
            current_network = {}

    return networks

# program start
logging.basicConfig(level=logging.DEBUG)
client = mqtt.Client(client_id="PiProgram")
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, broker_port, 60)

client.loop_forever()
