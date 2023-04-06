"""A dynmic select to get the wanted mosaic."""

import ipyvuetify as v
from ipywidgets import jslink
from sepal_ui import color as sc
from traitlets import Bool

from component.message import cm


class DynamicSelect(v.Layout):

    disabled = Bool(True).tag(sync=True)

    def __init__(self):
        """A composite widget to select mosaic by name."""
        self.prev = v.Btn(
            _metadata={"increm": -1},
            x_small=True,
            class_="ml-2 mr-2",
            color=sc.primary,
            children=[v.Icon(children=["mdi-chevron-left"]), cm.dynamic_select.prev],
        )

        self.next = v.Btn(
            _metadata={"increm": 1},
            x_small=True,
            class_="ml-2 mr-2",
            color=sc.primary,
            children=[cm.dynamic_select.next, v.Icon(children=["mdi-chevron-right"])],
        )

        self.select = v.Select(dense=True, label=cm.dynamic_select.label, v_model="")

        super().__init__(
            v_model="",
            align_center=True,
            row=True,
            class_="ma-1",
            children=[self.prev, self.select, self.next],
        )

        # js behaviour
        jslink((self, "v_model"), (self.select, "v_model"))
        self.prev.on_event("click", self._on_click)
        self.next.on_event("click", self._on_click)
        jslink((self, "disabled"), (self.prev, "disabled"))
        jslink((self, "disabled"), (self.next, "disabled"))
        jslink((self, "disabled"), (self.select, "disabled"))

    def set_items(self, items):
        """Change the value of the items of the select."""
        self.select.items = items
        self.disabled = False

        return self

    def _on_click(self, widget, event, data):
        """go to the next value. loop to the first or last one if we reach the end."""
        increm = widget._metadata["increm"]

        # create a sanitized version of the item list without the header
        items = [i["value"] for i in self.select.items if "header" not in i]

        # get the current position in the list
        val = self.select.v_model
        if val in items:
            pos = items.index(val)
            pos += increm

            # check if loop is required
            if pos == -1:
                pos = len(items) - 1
            elif pos >= len(items):
                pos = 0

        # if none was selected always start by the first
        else:
            pos = 0

        self.select.v_model = items[pos]

        return self
