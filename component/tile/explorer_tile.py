import ipyvuetify as v

from sepal_ui import sepalwidgets as sw 
from sepal_ui import mapping as sm

from component import widget as cw
from component import scripts as cs

class ExplorerTile(sw.Tile):
    
    def __init__(self):
        
        # gather the io 
        
        # create the widgets 
        self.api_key = cw.CustomPassword()
        self.check_key = sw.Btn('check', block = True)
        self.api_alert = sw.Alert()
        self.select = cw.DynamicSelect()
        self.m = cw.DownMap()
        txt = v.Html(tag='p', children=['I have plenty of room for explainations'])
        
        # create a layout 
        layout = v.Layout(
            row = True,
            align_center = True,
            children = [
                v.Flex(xs3=True, class_ = "ma-2", children = [txt, v.Divider(class_='mb-3'), self.api_key, self.check_key, self.api_alert]),
                v.Flex(children = [self.select, self.m])
            ]
        )
        
        # inster everything in the tile
        super().__init__(
            'explorer_tile',
            "Explore planet data",
            inputs = [layout]
        )
        
        # add js behaviour
        self.check_key.on_event('click', self._get_mosaic)
        
    def _get_mosaic(self, widget, event, data):
        """recover all the available mosaic with this specific key"""
        
        widget.toggle_loading()
        
        #try: 
        items = cs.order_basemaps(self.api_key.v_model, self.api_alert)
        self.select.set_items(items)
            
        #except Exception as e:
        #    self.api_alert.add_msg(str(e), 'error')
            
        widget.toggle_loading()
        
        return self
    
        
        