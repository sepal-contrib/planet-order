from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw
from sepal_ui.aoi import AoiModel
from sepal_ui.planetapi import PlanetModel
from sepal_ui.scripts import decorator as sd

from component import model as cmod
from component import scripts as cs
from component.message import cm


class DownView(sw.Tile):

    grid = None
    "the grod associated to the aoi"

    def __init__(
        self,
        aoi_model: AoiModel,
        planet_model: PlanetModel,
        order_model: cmod.OrderModel,
    ):

        # save models as members
        self.aoi_model = aoi_model
        self.planet_model = planet_model
        self.order_model = order_model

        super().__init__(
            "nested",
            cm.down_control.title,
            btn=sw.Btn(cm.down_control.btn, "fa-solid fa-cloud-arrow-down"),
            alert=sw.Alert().add_msg("Information"),
        )

        self.btn.on_event("click", self.download_quads)
        self.aoi_model.observe(lambda *args: setattr(self, "grid", None), "name")

    @sd.loading_button(debug=True)
    def download_quads(self, *args) -> None:

        if not self.aoi_model.name:
            raise Exception(cm.down_control.error.no_aoi)

        # load the planet grid
        if self.grid is None:
            self.alert.add_msg(cm.down_control.process.loading_grid)
            self.grid = cs.set_grid(self.aoi_model)

        # start the download process
        cs.download_quads(
            aoi_model=self.aoi_model,
            planet_model=self.planet_model,
            order_model=self.order_model,
            grid=self.grid,
            alert=self.alert,
        )


class DownControl(sm.MenuControl):
    def __init__(
        self,
        m: sm.SepalMap,
        aoi_model: AoiModel,
        planet_model: PlanetModel,
        order_model: cmod.OrderModel,
        **kwargs
    ):

        self.view = DownView(aoi_model, planet_model, order_model)

        # create the control
        super().__init__(
            icon_content="fa-solid fa-cloud-arrow-down",
            card_content=self.view,
            m=m,
            **kwargs
        )
        self.set_size(400, 400, None, None)
