#md8a.py

from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior 
from kivy.uix.popup import Popup
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.metrics import dp

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

class SSIDList(RecycleView):
    def __init__(self, **kwargs):
        super(SSIDList, self).__init__(**kwargs)
        #self.data = []
        ssids = [
            {"ssid": "Network 1", "signal": -60},
            {"ssid": "Network 2", "signal": -70},
            {"ssid": "Network 3", "signal": -80}
        ]

        #self.data = [{'text': f"{ssid['ssid']}...", 'selectable': True} for ssid in ssids]
        self.viewclass = 'SelectableLabel'
        self.data = [{'text': str(x)} for x in range(10)]

        self.layout_manager = RecycleGridLayout(cols=1, spacing=10, size_hint_y=None, orientation='lr-tb')
        self.layout_manager.bind(minimum_height=self.layout_manager.setter('height'))
        self.layout_manager.default_size = None, dp(56)
        self.layout_manager.default_size_hint = 1, None

        #self.viewclass = 'Label'
        #self.layout = RecycleGridLayout(cols=1, spacing=10, size_hint_y=None)
        #self.layout.size_hint_y = 0.8
        #self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout_manager)
        
        for i in range(10):
            self.data.append({'text': f'Item {i}'})
        
       # for ssid in ssids:
        #    self.data.append({'text': f"{ssid['ssid']} ({ssid['signal']} dBm)", 'selectable': True})
            
    def show_password_popup(self, ssid):
        popup = PasswordPopup(ssid) 
        popup.open()
        
class PasswordPopup(Popup):
    def __init__(self, ssid, **kwargs):
        super().__init__(**kwargs)
        self.ssid = ssid
        self.title = f"Enter password for {ssid}"
        # TODO: Add password entry, validation and submit logic
        
class MainApp(App):
    def build(self):
        return SSIDList()
        
MainApp().run()