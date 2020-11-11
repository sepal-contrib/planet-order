# planet-order
ordering planet data


## Usage

first download the repository to your own sepal account 

```
git clone https://github.com/12rambau/planet-order.git
```

In the `planet-order` folder, copy paste the `parameters.py.dist` file and remove the `.dist` extention 

```
cp parameters.py.dist parameters.py
```

You'll need to change the values of the parameters according to your needs. 
- **PLANET_API_KEY**: Your personal key to access the planet API
- **BASEMAP_URL**: The basemap you want to use (defaulted to `'https://api.planet.com/basemaps/v1/mosaics/'`)

Then in the `planet-order` folder, launch the `ui.ipynb` notebook and run it with voila.

> :warning: If for some reason the sepal_ui module doesn't work on your instance, you can run the `no_ui.ipynb` file as a notebook using `kernel->run all`
