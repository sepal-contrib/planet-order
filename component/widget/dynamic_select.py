from sepal_ui import sepalwidgets as sw 
import ipyvuetify as v
from ipywidgets import jslink

from component.message import cm

class DynamicSelect(v.Layout):
    
    def __init__(self):
        
        self.prev = v.Btn(
            _metadata = {'increm': -1},
            x_small = True,
            class_ = 'ml-2 mr-2',
            color = v.theme.themes.dark.secondary,
            children = [
                v.Icon(children = ['mdi-chevron-left']),
                cm.dynamic_select.prev
            ]
        )
        
        self.next = v.Btn(
            _metadata = {'increm': 1},
            x_small = True,
            class_ = 'ml-2 mr-2',
            color = v.theme.themes.dark.secondary,
            children = [
                cm.dynamic_select.next,
                v.Icon(children = ['mdi-chevron-right'])
            ]
        )
        
        self.select = v.Select(
            dense = True,
            label = cm.dynamic_select.label,
            v_model = None
        )
        
        super().__init__(
            v_model = None,
            align_center = True,
            row = True,
            class_ = 'ma-1',
            children = [
                self.prev, 
                self.select,
                self.next
            ]
        )
        
        # js behaviour
        jslink((self, 'v_model'), (self.select, 'v_model'))
        self.prev.on_event('click', self._on_click)
        self.next.on_event('click', self._on_click)
        
        
    def set_items(self, items):
        """Change the value of the items of the select"""
        
        self.select.items = items
        
        return self
    
    def _on_click(self, widget, event, data):
        """go to the next value. loop to the first or last one if we reach the end"""
        
        increm = widget._metadata['increm']
        
        # get the current position in the list 
        val = self.select.v_model
        if val in self.select.items:
            pos = self.select.items.index(val)
            
            pos += increm
            
            # check if loop is required
            if pos == -1:
                pos = len(self.select.items)-1
            elif pos >= len(self.select.items):
                pos = 0
                
        # if none was selected always start by the first
        else: 
            pos = 0
            
        self.select.v_model = self.select.items[pos]
        
        return self
            
        
        
        
            