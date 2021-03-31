import ipyvuetify as v

from sepal_ui import sepalwidgets as sw 
from sepal_ui import mapping as sm

from component import widget as cw
from component import scripts as cs
from component.message import cm

class ExplorerTile(sw.Tile):
    
    def __init__(self, aoi_io):
        
        # gather the io 
        self.aoi_io = aoi_io
        
        self.mapped = False # to set if the map have already been zoomed on a specific region or not
        
        # create the widgets 
        self.api_key = cw.CustomPassword()
        self.check_key = sw.Btn('check', block = True)
        self.down_quads = sw.Btn('download', block = True, disabled = True, class_ = 'mt-5').hide()
        self.api_alert = sw.Alert()
        self.select = cw.DynamicSelect()
        self.m = cw.DownMap()
        txt = v.Html(tag='p', children=['I have plenty of room for explainations'])
        
        # create a layout 
        layout = v.Layout(
            row = True,
            align_center = True,
            children = [
                v.Flex(xs3=True, class_ = "ma-2", children = [txt, v.Divider(class_='mb-3'), self.api_key, self.check_key, self.down_quads, self.api_alert]),
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
        self.select.observe(self._on_mosaic_select, 'v_model')
        self.down_quads.on_event('click', self._download)
        self.m.observe(self._on_combo_change, 'combo')
        
    def _on_combo_change(self, change):
        """update the mosaic if the planet key is available"""
        
        if not (self.select.v_model and cs.planet.valid):
            return self
        
        cs.display_basemap(self.select.v_model, self.m, self.m.state, self.m.combo)
        
        # finish the state 
        self.m.state.add_msg(cm.map.done, done=True)
        
        return self
            
        
    def _get_mosaic(self, widget, event, data):
        """recover all the available mosaic with this specific key"""
        
        widget.toggle_loading()
        
        try: 
            items = cs.order_basemaps(self.api_key.v_model, self.api_alert)
            self.select.set_items(items)
            self.down_quads.show()
            
        except Exception as e:
            self.api_alert.add_msg(str(e), 'error')
            
        widget.toggle_loading()
        
        return self
    
    def _on_mosaic_select(self, change):
        """load the mosaics on the map and release the download btn"""
        
        ds = change['owner']
        
        # block all the btn 
        ds.prev.disabled = True
        ds.next.disabled = True
        ds.select.disabled = True
        
        # unable the btn 
        if change['new']:
            self.down_quads.disabled = False
            
        # update the map 
        if not self.mapped:
            self.m.zoom_ee_object(self.aoi_io.get_aoi_ee().geometry())
            
            # unsure that this operation is only carried out once
            self.mapped = True
            
        # add the aoi and center the map on it
        cs.display_on_map(self.m, self.aoi_io, self.m.state)
            
        # add the grid 
        self.grid = cs.set_grid(self.aoi_io, self.m, self.m.state)
            
        # display the mosaic on the map 
        cs.display_basemap(self.select.v_model, self.m, self.m.state, self.m.combo)
        
        # finish the state 
        self.m.state.add_msg(cm.map.done, done=True)
        
        # release the btn
        ds.prev.disabled = False
        ds.next.disabled = False
        ds.select.disabled = False
        
        return self
    
    def _download(self, widget, event, data):
        """download the selected quads using the selected mosaic"""
        
        widget.toggle_loading()
        
        try:
            cs.download_quads(self.aoi_io.get_aoi_name(), self.select.v_model, self.grid, self.api_alert)
        
        except Exception as e:
            self.api_alert.add_msg(str(e), 'error')
            
        widget.toggle_loading()
        
        return self
            
    
    
        
        