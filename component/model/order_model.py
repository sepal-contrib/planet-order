from sepal_ui import model
from traitlets import Any


class OrderModel(model.Model):

    order_index = Any(None).tag(sync=True)
    orders = Any(None).tag(sync=True)
    session = Any(None).tag(sync=True)
    quads = Any(None).tag(sync=True)
