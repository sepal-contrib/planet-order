from sepal_ui import sepalwidgets as sw 
from sepal_ui import mapping as sm

class ResultTile(sw.Tile):
    
    def __init__(self):
        
        # create the widgets 
        self.m = sm.SepalMap()
        
        super().__init__(
        'result_widget',
        "Download results",
        inputs = [self.m]
    )
        
        