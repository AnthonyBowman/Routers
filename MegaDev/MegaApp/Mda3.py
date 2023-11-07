import paho.mqtt.client as mqtt
import time

# MQTT broker details
broker_address = "127.0.0.1"  # Update with your Mosquitto broker's address
port = 1883

# Callback function for when the client connects to the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        # Subscribe to the "Response" channel
        client.subscribe("Response")
    else:
GET        print("Connection failed with code", rc)

# Callback function for when a message is received on the subscribed channel
def on_message(client, userdata, message):
    print(f"Received message on topic {message.topic}: {message.payload.decode()}")

# Create an MQTT client
client = mqtt.Client()

# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, port)

# Start the MQTT client loop in the background
client.loop_start()

try:
    while True:
        # Publish a message to the "Command" channel
        command = input("Enter a command: ")
        client.publish("Command", command)

except KeyboardInterrupt:
    # Gracefully disconnect and stop the MQTT client loop
    client.disconnect()
    client.loop_stop()
