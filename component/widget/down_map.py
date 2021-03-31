import ipyvuetify as v

from traitlets import HasTraits, Any
from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw
from ipyleaflet import WidgetControl
from ipywidgets import jslink

from component.message import cm 
from component import parameter as cp

class DownMap(sm.SepalMap, HasTraits):
    
    combo = Any('').tag(sync=True)
    
    def __init__(self):
        
        # create the extra widget
        self.state = sw.StateBar(done=True)
        self.color = v.ListItemGroup(v_model = None, children=[v.ListItem(children= [c], value=c) for c in cp.planet_colors[:3]])
        self.palette = v.Menu(
            value=False,
            v_slots=[{
                'name': 'activator',
                'variable': 'menu',
                'children': v.Btn(v_model = False, v_on='menu.on', color='primary', icon = True, children=[v.Icon(children=['mdi-palette'])])
            }],
            children = [v.List(dense=True, outlined=True, rounded=True, children=[self.color])]
        )
        
        # create the map 
        super().__init__()
        
        # add the widget to the map (as to left and right items)
        self.add_control(WidgetControl(widget=self.state, position='topleft'))
        self.add_control(WidgetControl(widget=self.palette, position='topleft'))
        
        # create jslinks
        jslink((self, 'combo'), (self.color, 'v_model'))