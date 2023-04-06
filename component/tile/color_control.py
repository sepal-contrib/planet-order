from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw

from component import model as cmod
from component import parameter as cp


class ColorControl(sm.MenuControl):
    def __init__(self, m: sm.SepalMap, order_model: cmod.OrderModel, **kwargs):

        self.view = sw.ListItemGroup(
            v_model=cp.planet_colors[0],
            children=[sw.ListItem(children=[c], value=c) for c in cp.planet_colors[:4]],
        )

        # create the control
        super().__init__(
            icon_content="fa-solid fa-palette",
            card_content=self.view,
            m=m,
            group=1,
            **kwargs
        )
        self.set_size(None, None, None, None)

        # bind to the model
        order_model.bind(self.view, "color")
