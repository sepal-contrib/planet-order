from pathlib import Path

default_planet_key = None

# if the planet_key file exist use a default_planet_key
planet_key_file = Path(__file__).parents[2].joinpath('planet.key')
if planet_key_file.is_file():
    
    with planet_key_file.open() as f:
        default_planet_key = f.read().strip()
        
planet_colors = [
    'rgb',
    'cir',
    'ndvi',
    'ndwi',
    'vari',
    'msavi2',
    'mtvi2',
    'tgi'
]