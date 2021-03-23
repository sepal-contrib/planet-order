from sepal_ui import sepalwidgets as sw
import ipyvuetify as v

from component.message import cm
from parameters import PLANET_API_KEY, BASEMAP_URL 

class DownloadTile(sw.Tile):
    
    def __init__(self, io, aoi_io, m):
        
        # gather the io 
        self.aoi_io = aoi_io
        self.io = io
        self.m = m

        # create the widgets 
        txt = sw.Markdown(cm.download.txt) 
        self.select = v.Select(items=[], label=cm.download.select, v_model=None)

        # bind to the io 
        self.output = sw.Alert() \
            .bind(self.select, self.io, 'order_index')
        
        # create the btn 
        self.btn = sw.Btn(cm.download.btn, disabled=True)
        
        super().__init__(
            "download_widget",
            "Download Mosaic",
            inputs = [txt, self.select],  
            output = self.output,
            btn = self.btn
        )
        
        # bind the js behaviour 
        self.btn.on_event('click', self._down_mosaic)
        
    def _down_mosaic(self, widget, event, data):
        
        widget.toggle_loading()

        # check input 
        if not self.output.check_input(self.aoi_io.get_aoi_ee(), cm.viz.no_aoi): return widget.toggle_loading()
        if not self.output.check_input(po_order_io.order_index, cm.order.no_order): return widget.toggle_loading()
 
        try:
            mosaic_path, grid_path = cs.run_download(PLANET_API_KEY, BASEMAP_URL, self.aoi_io, self.io, self.m, self.output)
            down_grid.set_url(str(grid_path))
        
        except Exception as e: 
            self.output.add_live_msg(str(e), 'error') 

        widget.toggle_loading()

        return self
        
        

        
    
    
    