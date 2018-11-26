import os
import datetime
import re
from API import API
from CeleryPy import log
from CeleryPy import move_absolute
from CeleryPy import execute_sequence

variable = {"name1":120, "derp":456}

class MyFarmware():

    def get_input_env(self):
        prefix = self.farmwarename.lower().replace('-','_') # my-Farmware -> my_farmware
        
        self.input_title = os.environ.get(prefix+"_title", '-') #va chercher la variable "my_farmware_title" dans l'environnement de l'os. Cette variable a été créée dans le manifest.
        self.input_debug = int(os.environ.get(prefix+"_debug", 2)) # valeur par defaut est mise à 2

        if self.input_debug >= 1:
            log('title: {}'.format(self.input_title), message_type='debug', title=self.farmwarename)
            log('debug: {}'.format(self.input_debug), message_type='debug', title=self.farmwarename)
        
    def __init__(self,farmwarename):
        self.farmwarename = farmwarename
        self.get_input_env()
        self.api = API(self)

    def check_celerypy(self,ret):
        try:
            status_code = ret.status_code
        except:
            status_code = -1
        try:
            text = ret.text[:100]
        except:
            text = ret
        if status_code == -1 or status_code == 200:
            if self.input_debug >= 1: log("{} -> {}".format(status_code,text), message_type='debug', title=self.farmwarename + ' check_celerypy')
        else:
            log("{} -> {}".format(status_code,text), message_type='error', title=self.farmwarename + ' check_celerypy')
            raise


    def move_absolute_point(self, x, y, z, spd):
            if self.input_debug >= 1: log('Move absolute: ' + str(x) + ", " + str(y) + ", " + str(z) + ", " + str(spd) , message_type='debug', title=str(self.farmwarename) + ' : move_absolute_point')
            if self.input_debug < 2: 
                self.check_celerypy(move_absolute(
                    location=[x,y,z],
                    offset=[0, 0, 0],
                    speed=spd))
    
    
    def run(self):
        self.move_absolute(0,0,100,10)
        
