from sepal_ui import mapping as sm
from sepal_ui import planetapi


class PlanetControl(sm.MenuControl):
    def __init__(self, m: sm.SepalMap, model: planetapi.PlanetModel, **kwargs):

        # set the view and adapt the card to be embeded
        self.view = planetapi.PlanetView(planet_model=model)
        self.view.class_list.add("ma-5")

        # init the control
        super().__init__(
            icon_content="fa-solid fa-globe", card_content=self.view, m=m, **kwargs
        )

        # customize its size
        self.set_size(None, "80vw", None, None)
