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

    def apply_filters(self, points, point_name='', openfarm_slug='', age_min_day=0, age_max_day=36500, meta_key='', meta_value='', min_x='none', max_x='none', min_y='none', max_y='none', pointer_type='Plant', plant_stage='none'):
        if self.input_debug >= 1: log(points, message_type='debug', title=str(self.farmwarename) + ' : load_points')
        filtered_points = []
        now = datetime.datetime.utcnow()
        for p in points:
            if p['pointer_type'].lower() == pointer_type.lower():
                b_meta = False
                if str(p['planted_at']).lower() == 'none' or str(p['planted_at']).lower() == None:
                    ref_date = p['created_at']
                else:
                    ref_date = p['planted_at']
                age_day = (now - datetime.datetime.strptime(ref_date, '%Y-%m-%dT%H:%M:%S.%fZ')).days
                if str(meta_key).lower() != 'none':
                    try:
                        if self.input_filter_meta_op.lower() == "none" or self.input_filter_meta_op.lower() == "==":
                            b_meta = ((p['meta'][meta_key]).lower() == meta_value.lower())
                        elif self.input_filter_meta_op == ">=":
                            b_meta = ((p['meta'][meta_key]) >= meta_value)
                        elif self.input_filter_meta_op == "<=":
                            b_meta = ((p['meta'][meta_key]) <= meta_value)
                        elif self.input_filter_meta_op == "<":
                            b_meta = ((p['meta'][meta_key]) < meta_value)
                        elif self.input_filter_meta_op == ">":
                            b_meta = ((p['meta'][meta_key]) > meta_value)
                        elif self.input_filter_meta_op == "!=":
                            b_meta = ((p['meta'][meta_key]).lower() != meta_value.lower())
                        elif self.input_filter_meta_op.lower() == "regex":
                            b_meta = bool(re.compile(meta_value).match(p['meta'][meta_key]))
                        elif self.input_filter_meta_op.lower() == "daysmax":
                            b_meta = bool((datetime.datetime.utcnow() - datetime.datetime.strptime(p['meta'][meta_key], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()/86400 <= int(meta_value))
                        elif self.input_filter_meta_op.lower() == "minutesmax":
                            b_meta = bool((datetime.datetime.utcnow() - datetime.datetime.strptime(p['meta'][meta_key], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()/60 <= int(meta_value))
                        elif self.input_filter_meta_op.lower() == "daysmin":
                            b_meta = bool((datetime.datetime.utcnow() - datetime.datetime.strptime(p['meta'][meta_key], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()/86400 >= int(meta_value))
                        elif self.input_filter_meta_op.lower() == "minutesmin":
                            b_meta = bool((datetime.datetime.utcnow() - datetime.datetime.strptime(p['meta'][meta_key], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()/60 >= int(meta_value))
                        else:
                            b_meta = False
                    except Exception as e:
                        if self.input_debug >= 1: log(e, message_type='error', title=str(self.farmwarename) + ' : exception filter_meta')
                        b_meta = False
                else:
                    b_meta = True
                if str(min_x).lower() == 'none' or str(max_x).lower() == 'none':
                    b_coordinate_x = True
                else:
                    if int(min_x) <= int(p['x']) <= int(max_x):
                        b_coordinate_x = True
                    else:
                        b_coordinate_x = False
                if str(min_y).lower() == 'none' or str(max_y).lower() == 'none':
                    b_coordinate_y = True
                else:
                    if int(min_y) <= int(p['y']) <= int(max_y):
                        b_coordinate_y = True
                    else:
                        b_coordinate_y = False
                if plant_stage.lower() == 'none':
                    b_plantstage = True
                else:
                    try:
                        if plant_stage.lower() == p['plant_stage'].lower():
                            b_plantstage = True
                        else:
                            b_plantstage = False
                    except Exception as e:
                        b_plantstage = True
                if  (p['name'].lower() == point_name.lower() or point_name == '*') and (p['openfarm_slug'].lower() == openfarm_slug.lower() or openfarm_slug == '*') and (age_min_day <= age_day <= age_max_day) and b_meta==True and b_coordinate_x and b_coordinate_y and b_plantstage:
                    filtered_points.append(p.copy())
        return filtered_points

    def load_points_with_filters(self):
        self.points = self.apply_filters(
            points=self.api.api_get('points'),
            point_name=self.input_pointname,
            openfarm_slug=self.input_openfarm_slug,
            age_min_day=self.input_age_min_day,
            age_max_day=self.input_age_max_day,
            meta_key=self.input_filter_meta_key,
            meta_value=self.input_filter_meta_value,
            min_x=self.input_filter_min_x,
            min_y=self.input_filter_min_y,
            max_x=self.input_filter_max_x,
            max_y=self.input_filter_max_y,
            pointer_type='Plant',
            plant_stage=self.input_filter_plant_stage)
        if self.input_debug >= 1: log(self.points, message_type='debug', title=str(self.farmwarename) + ' : load_points_with_filters')
        

    def sort_points(self):
        self.points = sorted(self.points , key=lambda elem: (int(elem['x']), int(elem['y'])))
        if self.input_debug >= 1: log(self.points, message_type='debug', title=str(self.farmwarename) + ' : sort_points')
        #self.points, self.tab_id = Get_Optimal_Way(self.points)

    def load_sequences_id(self):
        self.sequences = self.api.api_get('sequences')
        self.input_sequence_init_dic = {}
        self.input_sequence_beforemove_dic = {}
        self.input_sequence_aftermove_dic = {}
        self.input_sequence_end_dic = {}
        for s in self.sequences:
            for e in self.input_sequence_init:
                if str(s['name']).lower() == e.lower() : self.input_sequence_init_dic[s['name']] = int(s['id'])
            for e in self.input_sequence_beforemove:
                if str(s['name']).lower() == e.lower() : self.input_sequence_beforemove_dic[s['name']] = int(s['id'])
            for e in self.input_sequence_aftermove:
                if str(s['name']).lower() == e.lower() : self.input_sequence_aftermove_dic[s['name']] = int(s['id'])
            for e in self.input_sequence_end:   
                if str(s['name']).lower() == e.lower() : self.input_sequence_end_dic[s['name']] = int(s['id'])    
        if self.input_debug >= 1:
            log('init: {}'.format(self.input_sequence_init_dic), message_type='debug', title=str(self.farmwarename) + ' : load_sequences_id')
            log('before: {}'.format(self.input_sequence_beforemove_dic) , message_type='debug', title=str(self.farmwarename) + ' : load_sequences_id')
            log('after: {}'.format(self.input_sequence_aftermove_dic) , message_type='debug', title=str(self.farmwarename) + ' : load_sequences_id')
            log('end: {}'.format(self.input_sequence_end_dic), message_type='debug', title=str(self.farmwarename) + ' : load_sequences_id')
    
    def execute_sequence_init(self):
        if len(self.input_sequence_init_dic) != 0:
            for s in self.input_sequence_init_dic:
                if self.input_debug >= 1: log('Execute Sequence: {} id: {}'.format(s,self.input_sequence_init_dic[s]), message_type='debug', title=str(self.farmwarename) + ' : execute_sequence_init')
                if self.input_debug < 2: self.check_celerypy(execute_sequence(sequence_id=self.input_sequence_init_dic[s]))
        else:
            if self.input_debug >= 1: log('Sequence Not Found', message_type='debug', title=str(self.farmwarename) + ' : execute_sequence_init')

    def execute_sequence_before(self):
        if len(self.input_sequence_beforemove_dic) != 0:
            for s in self.input_sequence_beforemove_dic:
                if self.input_debug >= 1: log('Execute Sequence: {} id: {}'.format(s,self.input_sequence_beforemove_dic[s]), message_type='debug', title=str(self.farmwarename) + ' : execute_sequence_before')
                if self.input_debug < 2: self.check_celerypy(execute_sequence(sequence_id=self.input_sequence_beforemove_dic[s]))
        else:
            if self.input_debug >= 1: log('Sequence Not Found', message_type='debug', title=str(self.farmwarename) + ' : execute_sequence_before')
                

    def execute_sequence_after(self):
        if len(self.input_sequence_aftermove_dic) != 0:
            for s in self.input_sequence_aftermove_dic:
                if self.input_debug >= 1: log('Execute Sequence: {} id: {}'.format(s,self.input_sequence_aftermove_dic[s]), message_type='debug', title=str(self.farmwarename) + ' : execute_sequence_after')
                if self.input_debug < 2: self.check_celerypy(execute_sequence(sequence_id=self.input_sequence_aftermove_dic[s]))
        else:
            if self.input_debug >= 1: log('Sequence Not Found', message_type='debug', title=str(self.farmwarename) + ' : execute_sequence_after')


    def execute_sequence_end(self):
        if len(self.input_sequence_end_dic) != 0:
            for s in self.input_sequence_end_dic:
                if self.input_debug >= 1: log('Execute Sequence: {} id: {}'.format(s,self.input_sequence_end_dic[s]), message_type='debug', title=str(self.farmwarename) + ' : execute_sequence_end')
                if self.input_debug < 2: self.check_celerypy(execute_sequence(sequence_id=self.input_sequence_end_dic[s]))
        else:
            if self.input_debug >= 1: log('Sequence Not Found', message_type='debug', title=str(self.farmwarename) + ' : execute_sequence_end')

    def move_absolute_point(self,point):
            if self.input_debug >= 1: log('Move absolute: ' + str(point) , message_type='debug', title=str(self.farmwarename) + ' : move_absolute_point')
            if self.input_debug < 2: 
                self.check_celerypy(move_absolute(
                    location=[point['x'],point['y'] ,self.input_default_z],
                    offset=[self.input_offset_x, self.input_offset_y, 0],
                    speed=self.input_default_speed))

    def save_meta(self,point):
        if str(self.input_save_meta_key).lower() != 'none':
            if(self.input_save_meta_value.lower() == "#now#"):
                point['meta'][self.input_save_meta_key]=str(datetime.datetime.utcnow())
            else:
                point['meta'][self.input_save_meta_key]=self.input_save_meta_value
            if self.input_debug >= 1: log('Save Meta Information: ' + str(point) , message_type='debug', title=str(self.farmwarename) + ' : save_meta')
            if self.input_debug < 2 :
                endpoint = 'points/{}'.format(point['id'])
                self.api.api_put(endpoint=endpoint, data=point)
                    
    def save_plant_stage(self,point):
        if str(self.input_save_plant_stage).lower() == 'planned' or str(self.input_save_plant_stage).lower() == 'planted' or str(self.input_save_plant_stage).lower() == 'harvested':
            point['plant_stage'] = str(self.input_save_plant_stage).lower()
            if str(self.input_save_plant_stage).lower() == 'planted':
                point['planted_at'] = str(datetime.datetime.utcnow())
            if self.input_debug >= 1: log('Save Plant Stage: ' + str(point) , message_type='debug', title=str(self.farmwarename) + ' : save_plant_stage')
            if self.input_debug < 2 :
                endpoint = 'points/{}'.format(point['id'])
                self.api.api_put(endpoint=endpoint, data=point)
        else:
            log('Save Plant Stage: wrong value :' + str(point) , message_type='error', title=str(self.farmwarename) + ' : save_plant_stage')
    

    def loop_points(self):
        for p in self.points:
            self.execute_sequence_before()
            self.move_absolute_point(p)
            self.execute_sequence_after()
            self.save_meta(p)
            self.save_plant_stage(p)
    
    
    def run(self):
        self.load_points_with_filters()
        self.sort_points()
        if len(self.points) > 0 : self.load_sequences_id()
        if len(self.points) > 0 : self.execute_sequence_init()        
        if len(self.points) > 0 : self.loop_points()
        if len(self.points) > 0 : self.execute_sequence_end()
        