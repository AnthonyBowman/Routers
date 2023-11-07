# Megadish App - set up Megadish
#
import paho.mqtt.client as mqtt
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class MQTTClient(mqtt.Client):
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("Response")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        print("Received message: " + message)
        # Process the received Wi-Fi details here
        # For demonstration purposes, let's just print them
        ssid, password = message.split(",")
        print("SSID: " + ssid)
        print("Password: " + password)


class WiFiDetailsForm(BoxLayout):
    def __init__(self, **kwargs):
        super(WiFiDetailsForm, self).__init__(**kwargs)
        self.orientation = "vertical"

        self.ssid_input = TextInput(hint_text="Enter Wi-Fi SSID")
        self.add_widget(self.ssid_input)

        self.password_input = TextInput(hint_text="Enter Wi-Fi password", password=True)
        self.add_widget(self.password_input)

        self.submit_button = Button(text="Submit")
        self.submit_button.bind(on_press=self.send_wifi_details)
        self.add_widget(self.submit_button)

        self.list_button = Button(text="List")
        self.list_button.bind(on_press=self.list_wifi_details)
        self.add_widget(self.list_button)

    def send_wifi_details(self, *args):
        ssid = self.ssid_input.text
        password = self.password_input.text

        # Connect to the MQTT broker on the Raspberry Pi
        client = MQTTClient()
        client.connect("127.0.0.1", 1883, 60)

        # Publish the Wi-Fi details to the topic "wifi/details"
        client.publish("Command", "USER-CHOICE, " + ssid + "-" + password)
        print("Wi-Fi details sent to Raspberry Pi.")

        # Disconnect from the MQTT broker
        client.disconnect()

    def list_wifi_details(self, *args):
        client = MQTTClient(client_id="MegadishApp")
        client.on_connect = on_connect
        
        client.connect("127.0.0.1", 1883, 60)
        client.subscribe("Response")
        #client_disconnect()

    def display_ssids(self, ssids):
        self.root.clear_widgets()

        layout = BoxLayout(orientation="vertical")

        title_label = Label(text="Available SSIDs:")
        layout.add_widget(title_label)

        for ssid in ssids:
            ssid_label = Label(text=ssid)
            layout.add_widget(ssid_label)

        refresh_button = Button(text="Refresh", on_release=self.refresh_ssids)
        layout.add_widget(refresh_button)

        self.root.add_widget(layout)

class MyApp(App):
    def build(self):
        return WiFiDetailsForm()


if __name__ == "__main__":
    MyApp().run()
