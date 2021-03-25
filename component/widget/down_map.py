import ipyvuetify as v

from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw
from ipyleaflet import WidgetControl

from component.message import cm 

class DownMap(sm.SepalMap):
    
    def __init__(self):
        
        # create the extra widget
        self.state = sw.StateBar(done=True)
        
        # create the map 
        super().__init__()
        
        # add the widget to the map (as to left and right items)
        self.add_control(WidgetControl(widget=self.state, position='topleft'))