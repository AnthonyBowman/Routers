#mda9.py

import json
import queue
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import ListProperty

import threading
import time
import paho.mqtt.client as mqtt

global global_ssids
ssids = [
            {"ssid": "", "signal": 0},

        ]
global_ssids = ssids

Builder.load_string('''
#:import random random.random

<CustomScreen>:
    hue: random()
    canvas:
        Color:
            hsv: self.hue, .5, .3
        Rectangle:
            size: self.size

    Label:
        font_size: 42
        text: root.name

    Button:
        text: 'Next screen'
        size_hint: None, None
        pos_hint: {'right': 1}
        size: 150, 50
        on_release: root.manager.current = root.manager.next()

<SelectableLabel>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: (.0, 0.9, .1, .3) if self.selected else (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
<RV>:
    viewclass: 'SelectableLabel'
    SelectableRecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: False
        touch_multiselect: False

<RVScreen>:
    BoxLayout:
        orientation: "vertical"
        RV:
        Button:
            text: 'Refresh'
            size_hint: None, None
            size: 150, 50
            on_release: root.refresh()

''')


class CustomScreen(Screen):
    hue = NumericProperty(0)

class PasswordPopup(Popup):
    ssid = ""
    
    def __init__(self, ssid, **kwargs):
        super().__init__(**kwargs)
        self.ssid = ssid
        self.title = f"Enter password for {ssid}"
        
        layout = BoxLayout(orientation="vertical", spacing=10, size_hint=(.4, None))

        self.password_input = TextInput(multiline=False) 
        layout.add_widget(self.password_input)

        connect_btn = Button(text="Connect", on_release=self.connect)
        layout.add_widget(connect_btn)

        self.content = layout

    def connect(self, btn):
        print(f"Connecting to {self.ssid}")
        # TODO - connect logic

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            ssid = rv.data[index]['text']
            popup = PasswordPopup(ssid)
            popup.auto_dismiss = False
            popup.size_hint = (None, None)
            popup.size = (dp(500), dp(250))
            popup.open()
        else:
            print("selection removed for {0}".format(rv.data[index]))
       
class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        #self.data = [{'text': str(x)} for x in range(10)]
        #ssids = [
         #   {"ssid": "PiLab", "signal": -60},
        #    {"ssid": "LongBow", "signal": -70},
        #    {"ssid": "Megadish", "signal": -80}
        #]
        self.data = [{'text': f"{ssid['ssid']} ({ssid['signal']} dBm)"} for ssid in global_ssids]
        #self.data = [{'text': ssid['ssid']} for ssid in ssids]

class RVScreen(Screen):
    def refresh(self):
        self.app.send_command(self)
        time.sleep(0.5)
        self.data = [{'text': f"{ssid['ssid']} ({ssid['signal']} dBm)"}  for ssid in global_ssids]

    def mini_refresh(self):
      self.rv.data = [{'text': f"{ssid['ssid']} ({ssid['signal']} dBm)"}  for ssid in global_ssids]
        
    pass

class ScreenManagerApp(App):
    lp_global_ssids = ListProperty()

    def send_command(self, instance):
        # Example: Put a command in the input queue
        cmd = ("GET-AVAILABLE","")
        self.in_q.put(cmd)

    def update_message(self, message):
        # This method is called from the MQTT thread to update the UI
        # Use Clock.schedule_once to execute the UI-related code in the main thread
        Clock.schedule_once(lambda dt: self.show_received_profiles(message), 0)

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
        
        global_ssids = full_ssids
        self.lp_global_ssids = global_ssids
        
    
        #ssid_popup = SSIDListPopup(ssids=self.ssids, callback=self.connect_to_ssid)
        #ssid_popup.open()

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

    def build(self):
        # Create queues
        self.in_q = queue.Queue()
        self.out_q = queue.Queue()

        # Start MQTT worker thread
        self.mqtt_worker = MQTTWorker(self, self.in_q, self.out_q)
        self.mqtt_worker.start()

        self.send_command(self)

        self.rvscreen = RVScreen()
        self.rvscreen.app = self
        root = ScreenManager()
        #root.add_widget(CustomScreen(name='CustomScreen'))
        root.add_widget(self.rvscreen)
        return root
        
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

if __name__ == '__main__':
    ScreenManagerApp().run()