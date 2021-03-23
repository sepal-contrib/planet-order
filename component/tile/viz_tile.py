from sepal_ui import sepalwidgets as sw 

from component.message import cm
from component import scripts as cs

class VizTile(sw.Tile):
    
    def __init__(self, aoi_io, m, order_btn):
        
        # gather the io 
        self.aoi_io = aoi_io
        self.m = m
        self.order_btn = order_btn
        
        # create the widgets 
        txt = sw.Markdown(cm.viz.txt) 
        
        # create the tile
        super().__init__(
            "download_widget",
            "Check inputs",
            inputs = [txt],
            output = sw.Alert(),
            btn = sw.Btn(cm.viz.btn)
        )
            
        # bind the js behaviour 
        self.btn.on_event('click', self._viz_data)
            
    def _viz_data(self, widget, event, data):
            
        widget.toggle_loading()

        # check input 
        if not self.output.check_input(self.aoi_io.get_aoi_ee(), cm.order.no_aoi): return widget.toggle_loading()
    
        try:
    
            # write msg
            msg = cs.get_sum_up(self.aoi_io)
            self.output.add_msg(msg, 'warning')

            # release the second btn 
            self.order_btn.disabled = False
            
        except Exception as e:
            output.add_live_msg(str(e), 'error')
        
        widget.toggle_loading()

        return self 

