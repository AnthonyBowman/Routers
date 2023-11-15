#Mda7.py
import json
import queue

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
from kivy.metrics import dp
import threading
import time
import paho.mqtt.client as mqtt

class SelectableRecycleBoxLayout(RecycleBoxLayout):
    def __init__(self, **kwargs):
        super(SelectableRecycleBoxLayout, self).__init__(**kwargs)
        self.default_size = None, dp(56)
        self.default_size_hint = 1, None
        self.orientation = 'vertical'
        self.spacing = 5
        self.padding = [10, 10]

class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

class SSIDListPopup(Popup):
    def __init__(self, ssids, callback, **kwargs):
        super(SSIDListPopup, self).__init__(**kwargs)
        self.callback = callback

        self.rv = RecycleView(size_hint=(1, 0.9))
        self.add_widget(self.rv)
        self.rv.layout_manager = SelectableRecycleBoxLayout()

        self.rv.viewclass = 'SelectableLabel'
        ssids1 = [
            {"ssid": "EE WiFi", "signal": -64},
            {"ssid": "A&A Wifi", "signal": -64},
            {"ssid": "EE WiFi", "signal": -64},
            {"ssid": "", "signal": -64},
            {"ssid": "Megadish", "signal": -60}
        ]
        self.rv.data = [{'text': f"{ssid['ssid']} ({ssid['signal']} dBm)"} for ssid in ssids1]
        #for ssid in ssids:
        #    for item in ssid:                
        #        self.rv.data = {'text': f"{item['ssid']} ({item['signal']} dBm)"} 
        #self.rv.data = [{'text': f"{ssid['ssid']} ({ssid['signal']} dBm)"} for ssid in ssids]
        
        box_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        #box_layout.add_widget(self.rv)

        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        btn_layout.add_widget(Button(text="Cancel", on_press=self.dismiss))
        btn_layout.add_widget(Button(text="Connect", on_press=self.connect_selected_ssid))
        box_layout.add_widget(btn_layout)

        self.content = box_layout

    def connect_selected_ssid(self, instance):
        selected_index = self.rv.layout_manager.selected_nodes[0]
        selected_ssid = self.rv.data[selected_index]['text'].split(' ')[0]
        self.callback(selected_ssid)
        self.dismiss()

class MQTTWorker(threading.Thread):
    def __init__(self, app_instance, in_q, out_q):
        super(MQTTWorker, self).__init__()
        self.app = app_instance
        self.in_q = in_q
        self.out_q = out_q

        # Initialize MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            Logger.info("Connected to MQTT broker successfully")
            # Subscribe to topics or perform other on-connect actions if needed
            client.subscribe("Response")
        else:
            Logger.error(f"Failed to connect to MQTT broker with result code {rc}")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        Logger.info(f"Received message: {message}")
        
        # Post the message to the main thread using Clock
        self.app.update_message(message)

    def run(self):
        # Connect to the MQTT broker
        self.client.connect("127.0.0.1", 1883, 60)

        # Start the network loop in a separate thread
        self.client.loop_start()

        while True:
            try:
                # Blocking call to get a command from the input queue
                #command = self.in_q.get()
                
                # Publish the command
                #self.client.publish("Command", command)

                command_tuple = self.in_q.get() # Gets command from Kivy       
                command_string = ",".join(map(str, command_tuple))
                self.client.publish("Command", command_string)                

                # Sleep for a short duration to allow processing of incoming messages
                time.sleep(0.1)

            except KeyboardInterrupt:
                break

        # Stop the network loop before exiting
        self.client.loop_stop()

class MyApp(App):
    def build(self):
        # Create queues
        self.in_q = queue.Queue()
        self.out_q = queue.Queue()

        # Start MQTT worker thread
        self.mqtt_worker = MQTTWorker(self, self.in_q, self.out_q)
        self.mqtt_worker.start()

        # Your application setup here
        self.button = Button(text="Send Command", on_press=self.send_command)
        return self.button

    def send_command(self, instance):
        # Example: Put a command in the input queue
        cmd = ("GET-AVAILABLE","")
        self.in_q.put(cmd)

    def update_message(self, message):
        # This method is called from the MQTT thread to update the UI
        # Use Clock.schedule_once to execute the UI-related code in the main thread
        Clock.schedule_once(lambda dt: self.show_received_profiles(message), 0)

    def show_alert(self, text):
        # This method is called in the main thread to show the alert
        content = Label(text=text)
        popup = Popup(title='Alert', content=content, size_hint=(None, None), size=(400, 200))
        popup.open()

    def connect_to_ssid(self, ssid):
        # Implement your logic to send SSID name and password to the server
        #password = self.get_password_from_user()  # Implement a method to prompt for password
        password = "Raspberry13"
        print(f"Connecting to SSID: {ssid} with password: {password}")
        self.send_command("CONNECTTO", "{ssid},{password}")

    def show_ssid_list(self):
        full_ssids = []

        for ssid in self.ssids:
            for item in ssid:
                if "ssid" in item and item["ssid"]:
                    full_ssids.append(ssid)
                    break

        if not full_ssids:
            print("No SSIDs with 'ssid' key available.")
            return
        
        ssid_popup = SSIDListPopup(ssids=self.ssids, callback=self.connect_to_ssid)
        ssid_popup.open()

    def show_received_profiles(self, text):
        # Assuming 'text' is a string representing JSON data
        try:
            received_ssids = json.loads(f"[{text}]")
            self.ssids = received_ssids
            print("Received SSIDs:", self.ssids)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

        # Now you can use self.ssids in your application as needed
        # For example, you can update the SSID list in the RecycleView or perform other operations
        self.show_ssid_list()

if __name__ == "__main__":
    MyApp().run()
