import os
from farmware_tools import log
from farmware_tools import 

class MyFarmware():
        
    def __init__(self,farmwarename):
        self.farmwarename = farmwarename

    def move(self,point, spd):
        log("going to " + point, message_type='debug')
    
    
    def run(self):
        log("test", message_type='debug')
        self.move([-100, -100, 50], 1)
        
