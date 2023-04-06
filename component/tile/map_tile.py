"""The map displayed in the map application."""

from ipyleaflet import TileLayer, WidgetControl
from sepal_ui import aoi, planetapi
from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw

from component import model as cmod
from component import scripts as cs

from .aoi_control import AoiControl
from .order_control import OrderControl
from .planet_control import PlanetControl


class MapTile(sw.Tile):
    def __init__(self):
        """Specific Map integrating all the widget components.

        Use this map to gather all your widget and place them on it. It will reduce the amount of work to perform in the notebook
        """
        # create a map
        self.m = sm.SepalMap(zoom=3)  # to be visible on 4k screens

        # create the model here as it will be easier to share between controls
        self.aoi_model = aoi.AoiModel(gee=True)
        self.planet_model = planetapi.PlanetModel()
        self.order_model = cmod.OrderModel()

        # create the controls
        fullscreen_control = sm.FullScreenControl(
            self.m, True, True, position="topright"
        )
        aoi_control = AoiControl(self.m, self.aoi_model)
        planet_control = PlanetControl(self.m, self.planet_model)
        order_control = OrderControl(
            self.m, self.order_model, self.planet_model, position="topleft"
        )

        # place them on the map
        self.m.add(fullscreen_control)
        self.m.add(planet_control)
        self.m.add(aoi_control)
        self.m.add(order_control)

        # create the tile
        super().__init__("map_tile", "", [self.m])

        # add js behaviour
        self.order_model.observe(self.display_mosaic, "mosaic")

    def display_mosaic(self, *args) -> None:
        """display the mosaic when one of the parameter is changed"""

        if not (self.order_model.mosaic or self.planet_model.active):
            return

        # create a new Tile layer on the map
        layer = TileLayer(
            url=cs.get_url(self.planet_model, self.order_model.mosaic, "visual"),
            name="Planet© Mosaic",
            attribution="Imagery © Planet Labs Inc.",
            show_loading=True,
        )
        self.m.add_layer(layer)

        return

    def set_code(self, link):
        """Add the code link btn to the map."""
        btn = sm.MapBtn("fa-solid fa-code", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.m.add(control)

        return

    def set_wiki(self, link):
        """Add the wiki link btn to the map."""
        btn = sm.MapBtn("fa-solid fa-book-open", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.m.add(control)

        return

    def set_issue(self, link):
        """Add the code link btn to the map."""
        btn = sm.MapBtn("fa-solid fa-bug", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.m.add(control)

        return
