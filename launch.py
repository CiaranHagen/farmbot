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
    
    log("Farmware running...", message_type='info')
    
    s = Sequence("1", "green")
    s.add(farmware.move(100, 100, -100, 50))
    s.add(farmware.move(150, 150, -50, 50))
    x = send_celery_script(cp.create_node(kind='execute', args=s.sequence))
    farmware = MyFarmware(FARMWARE_NAME)    
    log("test 2", message_type='info')

    a = Sequence("2", "green")
    a.add(farmware.move(100, 100, -100, 50))
    send_celery_script(cp.create_node(kind='execute', args=a.sequence))
    
    log("test finish", message_type='info')
    farmware.s = Structure()
    log("Data loaded.", message_type='info')
    
    log("Test successful.", message_type='info')
    farmware.s.moveRel(100,100,100,50)
    
if __name__ == "__main__":
    main()
