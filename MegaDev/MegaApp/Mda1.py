from kivy.app import App
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
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

        # MQTT setup
        self.mqtt_client = Client()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("192.168.17.101", 1883, 60)
        
        # Send "GET-SSIDS" message to request SSID list
        self.mqtt_client.publish("CommandChannel", "GET-SSIDS,0")

        self.mqtt_client.subscribe("CommandChannel")

        return self.layout

    def on_message(self, client, userdata, message):
        # Callback for MQTT message reception
        # Extract and display SSID list received over MQTT
        ssids = message.payload.decode("utf-8").split(",")
        for ssid in ssids:
            btn = Button(text=ssid, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.ssid_button.setter('text')(btn.text))
            self.dropdown.add_widget(btn)

    def on_ssid_select(self, instance, value):
        # Callback when an SSID is selected from the dropdown
        selected_ssid = value
        print(f"Selected SSID: {selected_ssid}")

if __name__ == "__main__":
    SSIDListApp().run()
