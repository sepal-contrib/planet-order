import ipyvuetify as v

from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw
from ipyleaflet import WidgetControl

from component.message import cm 

class DownMap(sm.SepalMap):
    
    def __init__(self):
        
        # create the extra widgets 
        self.state = sw.StateBar(done=True)
        self.down_btn = v.Btn(
            small = True,
            children = [v.Icon(class_ = "ma-1", children=['mdi-download'])]
        )
        
        # create the map 
        super().__init__()
        
        # add the widget to the map (as to left and right items)
        controls = [
            WidgetControl(widget=self.down_btn, position='topright', transparent_bg=True),
            WidgetControl(widget=self.state, position='topleft')
        ] + list(self.controls)
        self.controls = tuple(controls)