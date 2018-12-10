import os
from FARMWARE import MyFarmware
from FARMWARE import Sequence
from farmware_tools import log
import CeleryPy as cp
from structure import Structure
from farmware_tools import send_celery_script

FARMWARE_NAME = "jhempbot"
"""
def get_env(key, type_=str):
    return type_(os.environ["{}_{}".format(FARMWARE_NAME, key)])
"""
def main():
    log("jhempbot --> hello")
    farmware = MyFarmware(FARMWARE_NAME)
    farmware.run()
    
if __name__ == "__main__":
    main()
