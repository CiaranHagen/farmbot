import os
from farmware_tools import log
from farmware_tools import 

class MyFarmware():
        
    def __init__(self,farmwarename):
        self.farmwarename = farmwarename

    def move_absolute_point(self,point, spd):
            log("goint to " + point, message_type='debug', title=self.farmwarename)
    
    
    def run(self):
        log("test", message_type='debug', title=self.farmwarename)
        self.move_absolute([-100, -100, 50], 1)
        
