from pathlib import Path

def get_default_result_dir():
    """create the default result dir of this repository"""
    
    result_dir = Path('~', 'downloads', 'planet').expanduser()
    result_dir.mkdir(exist_ok=True)
    
    return result_dir

def get_result_dir(aoi_name):
    
    result_dir = get_default_result_dir().joinpath(aoi_name)
    
    result_dir.mkdir(exist_ok=True)
    
    return result_dir