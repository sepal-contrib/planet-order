"""The explorer tile."""

import ipyvuetify as v
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su

from component import scripts as cs
from component import widget as cw
from component.message import cm


class ExplorerTile(sw.Tile):
    def __init__(self, aoi_model):
        """The explorer tile."""
        # gather the io
        self.aoi_model = aoi_model

        # create the widgets
        self.api_key = cw.CustomPassword()
        self.check_key = sw.Btn(cm.planet.btn.check, block=True)
        self.down_quads = sw.Btn(
            cm.planet.btn.download, block=True, disabled=True, class_="mt-5"
        ).hide()
        self.api_alert = sw.Alert()
        self.select = cw.DynamicSelect()
        self.m = cw.DownMap()

        # create a layout
        layout = v.Layout(
            row=True,
            align_center=True,
            children=[
                v.Flex(
                    xs3=True,
                    class_="ma-2",
                    children=[
                        self.api_key,
                        self.check_key,
                        self.down_quads,
                        self.api_alert,
                    ],
                ),
                v.Flex(children=[self.select, self.m]),
            ],
        )

        # inster everything in the tile
        super().__init__("explorer_tile", cm.planet.title, inputs=[layout])

        # decorate the functions
        self._get_mosaic = su.loading_button(
            button=self.check_key, alert=self.api_alert, debug=True
        )(self._get_mosaic)
        self._download = su.loading_button(
            button=self.down_quads, alert=self.api_alert, debug=True
        )(self._download)

        # add js behaviour
        self.check_key.on_event("click", self._get_mosaic)
        self.select.observe(self._on_mosaic_select, "v_model")
        self.down_quads.on_event("click", self._download)
        self.m.observe(self._on_combo_change, "combo")
        self.aoi_model.observe(self._update_aoi, "name")

    def _update_aoi(self, change):
        """update the aoi when it's changed in the aoi_selector."""
        if change["new"] is None:
            return

        # add the aoi and center the map on it
        cs.display_on_map(self.m, self.aoi_model, self.m.state)
        self.m.zoom_bounds(self.aoi_model.total_bounds())

        # reset the mosaic selection if needed
        self.select.select.v_model = None

        # disabled the quad download as well
        self.down_quads.disabled = True

        return

    def _on_combo_change(self, change):
        """update the mosaic if the planet key is available."""
        if not (self.select.v_model and cs.planet.valid):
            return self

        cs.display_basemap(self.select.v_model, self.m, self.m.state, self.m.combo)

        # finish the state
        self.m.state.add_msg(cm.map.done, loading=False)

        return self

    def _get_mosaic(self, widget, event, data):
        """recover all the available mosaic with this specific key."""
        items = cs.order_basemaps(self.api_key.v_model, self.api_alert)
        self.select.set_items(items)
        self.down_quads.show()

        self.select.disabled = False  # unable()

        return self

    @su.switch("disabled", on_widgets=["select"])
    def _on_mosaic_select(self, change):
        """load the mosaics on the map and release the download btn."""
        if change["new"] is None:
            return

        # block all the btn
        # self.select.disable()

        # unable the btn
        self.down_quads.disabled = False

        # add the grid
        self.grid = cs.set_grid(self.aoi_model, self.m, self.m.state)

        # display the mosaic on the map
        cs.display_basemap(self.select.v_model, self.m, self.m.state, self.m.combo)

        # finish the state
        self.m.state.add_msg(cm.map.done, loading=False)

        # release the btn
        # self.select.unable()

        return

    def _download(self, widget, event, data):
        """download the selected quads using the selected mosaic."""
        cs.download_quads(
            self.aoi_model.name, self.select.v_model, self.grid, self.api_alert
        )

        return self
