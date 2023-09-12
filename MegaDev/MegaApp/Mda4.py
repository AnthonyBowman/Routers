from kivy.app import App
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from paho.mqtt.client import Client

class SSIDListApp(App):
    def build(self):
        self.title = "SSID List"
        self.layout = BoxLayout(orientation="vertical")

        self.dropdown = DropDown()
        self.ssid_button = Button(text="Select SSID")
        self.ssid_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=self.on_ssid_select)

        self.layout.add_widget(Label(text="Available SSIDs:"))
        self.layout.add_widget(self.ssid_button)

        return self.layout

    def on_start(self):
        # MQTT setup
        self.mqtt_client = Client(client_id="kivy-client", clean_session=True)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("192.168.17.101", 1883, 60)

        # Start the MQTT loop in a new thread
        self.mqtt_client.loop_start()

        # Send "GET-SSIDS" message to request SSID list
        self.mqtt_client.publish("Command", "GET-SSIDS,0")

    def on_connect(self, client, userdata, flags, rc):
        # Callback for MQTT client connection
        if rc == 0:
            print("Connected to MQTT broker")
            client.subscribe("Response", 0)
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, message):
        # Callback for MQTT message reception
        # Extract and display SSID list received over MQTT
        ssids = message.payload.decode("utf-8").split(",")
        for ssid in ssids:
            # Schedule the creation of the button in the main Kivy thread
            Clock.schedule_once(lambda dt, s=ssid: self.create_button(s))

    def create_button(self, ssid):
        # This function is called in the main Kivy thread
        btn = Button(text=ssid, size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.ssid_button.setter('text')(self, btn.text))
        #btn.bind(on_release=lambda btn: self.ssid_button.setter('text')(btn.text))
        self.dropdown.add_widget(btn)

    def on_ssid_select(self, instance, value):
        # Callback when an SSID is selected from the dropdown
        selected_ssid = value
        print(f"Selected SSID: {selected_ssid}")

if __name__ == "__main__":
    SSIDListApp().run()
