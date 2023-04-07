from sepal_ui import mapping as sm
from sepal_ui import planetapi

from component import model as cmod
from component import scripts as cs
from component import widget as cw


class OrderControl(sm.MenuControl):
    def __init__(
        self,
        map_,
        order_model: cmod.OrderModel,
        planet_model: planetapi.PlanetModel,
        **kwargs
    ):

        # save needed member
        self.planet_model = planet_model
        self.order_model = order_model

        # create the view
        self.view = cw.DynamicSelect()
        self.view.class_list.add("ma-5")

        # create the control
        super().__init__(
            icon_content="fa-solid fa-folder", card_content=self.view, m=map_, **kwargs
        )

        self.set_size(None, None, None, None)

        # bindings
        self.order_model.bind(self.view, "mosaic")

        # add js behaviour
        self.planet_model.observe(self.get_mosaics, "active")

    def get_mosaics(self, *args) -> None:
        """add the mosaic items when a key is validated"""

        if self.planet_model.active is False:
            self.menu.v_model = False
            self.view.disabled = True
            return

        # set the values
        mosaics = self.planet_model.get_mosaics()
        self.view.set_items(cs.order_basemaps(mosaics))

        # open the menu
        self.menu.v_model = True
