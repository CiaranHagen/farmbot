import os
from farmware_tools import log
from farmware_tools import send_celery_script
import CeleryPy as cp

class MyFarmware():
        
    def __init__(self,farmwarename):
        self.farmwarename = farmwarename

    def move(self,point, spd):
        log("going to " + str(point), message_type='debug')
        send_celery_script(cp.move_absolute(location=[point[0], point[1], point[2]], offset=[0,0,0], speed=10))
    
    
    def run(self):
        log("test", message_type='debug')
        self.move([-100, -100, 50], 1)
        
