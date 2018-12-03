import os
from farmware_tools import log
from farmware_tools import send_celery_script
import CeleryPy as cp

class MyFarmware():
        
    def __init__(self,farmwarename):
        self.farmwarename = farmwarename

    def move(self, posx, posy, posz, spd):
        """
        pos = [x:Int ,y:Int ,z:Int]
        spd :Int
        """
        log("going to " + str(posx) + ", " + str(posy) + ", " + str(posz), message_type='debug')
        send_celery_script(cp.move_absolute(location=[posx, posy, posz], offset=[0,0,0], speed=spd))
    
    
    def run(self):
        log("test", message_type='debug')
        self.move(100, 100, -50, 10)
        
