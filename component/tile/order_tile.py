from sepal_ui import sepalwidgets as sw

from component.message import cm
from parameters import PLANET_API_KEY, BASEMAP_URL
from component import scripts as cs

class OrderTile(sw.Tile):
    
    def __init__(self, aoi_io, io, down_btn, order_select):
        
        # gathe the io 
        self.io = io
        self.aoi_io = aoi_io
        self.down_btn = down_btn
        self.order_select = order_select
        
        # create the widgets
        order_txt = sw.Markdown(cm.order.txt) 
        
        super().__init__(
            "download_widget",
            "Order mosaic",
            inputs = [order_txt],
            output = sw.Alert(),
            btn = sw.Btn(cm.order.btn, disabled=True)
        )
        # bind the js behaviours
        self.btn.on_event('click', self._order_mosaic)
        
    def _order_mosaic(self, widget, event, data):
        
        widget.toggle_loading()

        # check input 
        if not self.output.check_input(self.aoi_io.get_aoi_ee(), cm.order.no_aoi): return widget.toggle_loading()
 
        try:
            # get the orders
            orders, session = cs.get_orders(PLANET_API_KEY, BASEMAP_URL, self.output)
            self.io.orders = orders
            self.io.session = session
        
            # construct a order dict with only the name and the index
            #orders = {order['name']: i for i, order in enumerate(orders)}
            self.order_select.items = [{'text': order['name'], 'value': i} for i, order in enumerate(orders)]
            self.down_btn.disabled = False
            
            # draw the grid on the map 
            #grid_path = cs.get_theorical_grid(self.aoi_io, self.m, self.output)
        
            self.output.add_live_msg('Orders list updated', 'success')
    
        except Exception as e: 
            self.output.add_live_msg(str(e), 'error') 

        widget.toggle_loading()
        
        return self