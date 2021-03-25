# this file will be used as a singleton object in the explorer tile 
import requests
from types import SimpleNamespace

from planet import api

from component.message import cm

planet = SimpleNamespace()

# parameters
planet.url = 'https://api.planet.com/auth/v1/experimental/public/my/subscriptions'

# attributes

planet.valid = False
planet.key = None
planet.client = None

def check_key():
    """raise an error if the key is not validataed"""
    
    if not planet.valid:
        raise Exception(cm.planet.invalid_key)
    
    return

def validate_key(key, out):
    """Validate the API key and save it the key variable"""
    
    out.add_msg(cm.planet.test_key)
    
    # get all the subscriptions 
    resp = requests.get(planet.url, auth=(key, ''))
    subs = resp.json()
    
    # only continue if the resp was 200
    if resp.status_code != 200:
        raise Exception(subs['message'])
    
    # check the subscription validity 
    # stop the execution if it's not the case
    planet.valid = any([True for sub in subs if sub['state'] == 'active'])
    check_key()
    
    planet.key = key
    
    out.add_msg(cm.planet.valid_key, 'success')
    
    return 

def order_basemaps(key, out):
    """check the apy key and then order the basemap to update the select list"""
    
    # checking the key validity
    validate_key(key, out)
    
    out.add_msg(cm.planet.load_mosaics)
    
    # autheticate to planet
    client = api.ClientV1(api_key=planet.key)
    
    # get the basemap names 
    mosaics = [m['name'] for m in client.get_mosaics().get()['mosaics']]
    
    out.add_msg(cm.planet.mosaic_loaded, 'success')
    
    return mosaics


    
    
    


    
    
    
    
    