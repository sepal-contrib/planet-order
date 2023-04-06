"""Model to order basemaps to NICFI."""

from sepal_ui import model
from traitlets import Any, Unicode


class OrderModel(model.Model):

    mosaic = Unicode("").tag(sync=True)
    "the current mosaic name"

    order_index = Any(None).tag(sync=True)
    orders = Any(None).tag(sync=True)
    session = Any(None).tag(sync=True)
    quads = Any(None).tag(sync=True)
