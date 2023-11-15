import paho.mqtt.client as mqtt

# MQTT broker details 
broker_address = "localhost"
broker_port = 1883

# Topics  
command_topic = "Command"
response_topic = "Response"

# Client callbacks
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
  print("Received: "+ msg.payload.decode())

# Create client and attach callbacks  
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
client.connect(broker_address, broker_port)

# Listen for responses
client.subscribe(response_topic)

# Publish command messages
client.publish(command_topic, "GET-AVAILABLE,data")
#client.publish(command_topic, "GET-STORED,data")

# Blocking loop to process network traffic
client.loop_forever()