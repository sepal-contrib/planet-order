# planet-order
ordering planet data


## Usage

first download the repository to your own sepal account 

```
git clone https://github.com/12rambau/planet-order.git
```

In the `planet-order` folder, copy paste the `planet.key.dist` file and remove the `.dist` extention 

```
cp planet.key.dist planet.key
```

You'll need to change the values of the parameters according to your needs. 
- **ThisIsNotAKey**: Your personal key to access the planet API

> :warning: The key that leaves in the `planet.key` file is used as the default key of the module. You can skip this step and use the key TextField to use your personnal.

Then in the `planet-order` folder, launch the `ui.ipynb` notebook and run it with voila.

> :warning: If for some reason the sepal_ui module doesn't work on your instance, you can run the `no_ui.ipynb` file as a notebook using `kernel->run all`
