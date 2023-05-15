"""Model to order basemaps to NICFI."""

from sepal_ui import model
from traitlets import Any, Unicode


class OrderModel(model.Model):

    mosaic = Unicode("").tag(sync=True)
    "the current mosaic name"

    color = Unicode("rgb").tag(sync=True)
    "the slected color"

    order_index = Any(None).tag(sync=True)
    orders = Any(None).tag(sync=True)
    session = Any(None).tag(sync=True)
    quads = Any(None).tag(sync=True)
