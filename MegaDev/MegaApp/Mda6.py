#Mda6.py

from kivy.app import App 
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger

import paho.mqtt.client as mqtt

from threading import Thread 
from queue import Queue
import time

out_q = Queue()
in_q = Queue()  

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    Logger.info(f"Connected with result code {rc}")
    client.show_alert(f"here 1")
    client.subscribe("Response")

class MainApp(App):

  def build(self):
    self.button = Button(text="List", on_press=self.list_networks)
    self.labels = []
    return self.button  

  def list_networks(self, instance):
    cmd = ("GET-AVAILABLE","")
    out_q.put(cmd)
    self.check_incoming(0)

  def check_incoming(self, dt):  
    while not in_q.empty():
      ssid = in_q.get()
      label = Label(text=ssid)
      self.labels.append(label)



def mqtt_worker(in_q, out_q):

    def on_connect(client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        Logger.info(f"Connected with result code {rc}")
        client.show_alert("here 1")
        client.subscribe("Response")
    

    def on_message(client, userdata, msg):
        message = msg.payload.decode("utf-8")
        print(f"Received message: {message}")
        Logger.info(f"Received message: {message}")

        in_q.put(message)

    client = mqtt.Client(client_id="MegadishApp")

    # Set callback functions
    client.on_connect = on_connect
    client.on_message = on_message
  
    client.connect("127.0.0.1", 1883, 60)

    while True:
        #response = client.subscribe("Response") # Wait for response

        command_tuple = out_q.get() # Gets command from Kivy       
        command_string = response_string = ",".join(map(str, command_tuple))
        client.publish("Command", command_string)

        #in_q.put(response) # Send back to Kivy

thread = Thread(target=mqtt_worker, args=(in_q, out_q))
thread.start()

app = MainApp()
app.run()

Clock.schedule_interval(app.check_incoming, 1) 


