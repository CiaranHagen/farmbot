import os
import datetime
import re
from API import API
from CeleryPy import log
from CeleryPy import move_absolute
from CeleryPy import execute_sequence

class MyFarmware():

    def get_input_env(self):
        prefix = self.farmwarename.lower().replace('-','_')
        
        self.input_title = os.environ.get(prefix+"_title", '-')
        self.input_pointname = os.environ.get(prefix+"_pointname", '*')
        self.input_openfarm_slug = os.environ.get(prefix+"_openfarm_slug", '*')
        self.input_age_min_day = int(os.environ.get(prefix+"_age_min_day", -1))
        self.input_age_max_day = int(os.environ.get(prefix+"_age_max_day", 36500))
        self.input_filter_meta_key = os.environ.get(prefix+"_filter_meta_key", 'None')
        self.input_filter_meta_op = os.environ.get(prefix+"_filter_meta_op", 'None')
        self.input_filter_meta_value = os.environ.get(prefix+"_filter_meta_value", 'None')
        self.input_filter_plant_stage = os.environ.get(prefix+"_filter_plant_stage", 'None')
        self.input_filter_min_x = os.environ.get(prefix+"_filter_min_x", 'None')
        self.input_filter_max_x = os.environ.get(prefix+"_filter_max_x", 'None')
        self.input_filter_min_y = os.environ.get(prefix+"_filter_min_y", 'None')
        self.input_filter_max_y = os.environ.get(prefix+"_filter_max_y", 'None')
        self.input_sequence_init = os.environ.get(prefix+"_sequence_init", 'None').split(",")
        self.input_sequence_beforemove  = os.environ.get(prefix+"_sequence_beforemove", 'None').split(",")
        self.input_sequence_aftermove = os.environ.get(prefix+"_sequence_aftermove", 'None').split(",")
        self.input_sequence_end = os.environ.get(prefix+"_sequence_end", 'None').split(",")
        self.input_save_meta_key = os.environ.get(prefix+"_save_meta_key", 'None')
        self.input_save_meta_value = os.environ.get(prefix+"_save_meta_value", 'None')
        self.input_save_plant_stage = os.environ.get(prefix+"_save_plant_stage", 'None')
        self.input_offset_x = int(os.environ.get(prefix+"_offset_x", 0))
        self.input_offset_y = int(os.environ.get(prefix+"_offset_y", 0))
        self.input_default_z = int(os.environ.get(prefix+"_default_z", 0))
        self.input_default_speed = int(os.environ.get(prefix+"_default_speed", 800))
        self.input_debug = int(os.environ.get(prefix+"_debug", 2))

        if self.input_debug >= 1:
            log('title: {}'.format(self.input_title), message_type='debug', title=self.farmwarename)
            log('pointname: {}'.format(self.input_pointname), message_type='debug', title=self.farmwarename)
            log('openfarm_slug: {}'.format(self.input_openfarm_slug), message_type='debug', title=self.farmwarename)
            log('age_min_day: {}'.format(self.input_age_min_day), message_type='debug', title=self.farmwarename)
            log('age_max_day: {}'.format(self.input_age_max_day), message_type='debug', title=self.farmwarename)
            log('filter_meta_key: {}'.format(self.input_filter_meta_key), message_type='debug', title=self.farmwarename)
            log('filter_meta_op: {}'.format(self.input_filter_meta_op), message_type='debug', title=self.farmwarename)
            log('filter_meta_value: {}'.format(self.input_filter_meta_value), message_type='debug', title=self.farmwarename)
            log('filter_plant_stage: {}'.format(self.input_filter_plant_stage), message_type='debug', title=self.farmwarename)
            log('filter_min_x: {}'.format(self.input_filter_min_x), message_type='debug', title=self.farmwarename)
            log('filter_max_x: {}'.format(self.input_filter_max_x), message_type='debug', title=self.farmwarename)
            log('filter_min_y: {}'.format(self.input_filter_min_y), message_type='debug', title=self.farmwarename)
            log('filter_max_y: {}'.format(self.input_filter_max_y), message_type='debug', title=self.farmwarename)
            log('sequence_init: {}'.format(self.input_sequence_init), message_type='debug', title=self.farmwarename)
            log('sequence_beforemove: {}'.format(self.input_sequence_beforemove), message_type='debug', title=self.farmwarename)
            log('sequence_aftermove: {}'.format(self.input_sequence_aftermove), message_type='debug', title=self.farmwarename)
            log('sequence_end: {}'.format(self.input_sequence_end), message_type='debug', title=self.farmwarename)
            log('save_meta_key: {}'.format(self.input_save_meta_key), message_type='debug', title=self.farmwarename)
            log('save_meta_value: {}'.format(self.input_save_meta_value), message_type='debug', title=self.farmwarename)
            log('save_plant_stage: {}'.format(self.input_save_plant_stage), message_type='debug', title=self.farmwarename)
            log('offset_x: {}'.format(self.input_offset_x), message_type='debug', title=self.farmwarename)
            log('offset_y: {}'.format(self.input_offset_y), message_type='debug', title=self.farmwarename)
            log('default_z: {}'.format(self.input_default_z), message_type='debug', title=self.farmwarename)
            log('default_speed: {}'.format(self.input_default_speed), message_type='debug', title=self.farmwarename)
            log('debug: {}'.format(self.input_debug), message_type='debug', title=self.farmwarename)
        
    def __init__(self,farmwarename):
        self.farmwarename = farmwarename
        self.get_input_env()
        self.api = API(self)
        self.points = []

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


    def move_absolute_point(self, x, y, z):
            if self.input_debug >= 1: log('Move absolute: ' + str(x) + ", " + str(y) + ", " + str(xz) , message_type='debug', title=str(self.farmwarename) + ' : move_absolute_point')
            if self.input_debug < 2: 
                self.check_celerypy(move_absolute(
                    location=[point['x'],point['y'] ,self.input_default_z],
                    offset=[self.input_offset_x, self.input_offset_y, 0],
                    speed=self.input_default_speed))
    
    
    def run(self):
        self.load_points_with_filters()
        self.sort_points()
        if len(self.points) > 0 : self.load_sequences_id()
        if len(self.points) > 0 : self.execute_sequence_init()        
        if len(self.points) > 0 : self.loop_points()
        if len(self.points) > 0 : self.execute_sequence_end()
