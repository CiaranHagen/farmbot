import os
from farmware_tools import log
from farmware_tools import send_celery_script
import CeleryPy as cp
from structure import PlantType, Plant, Pot, Region, Structure

class MyFarmware():  
    coords = [0,0,0]
    def __init__(self,farmwarename):
        self.farmwarename = farmwarename
    
    ##FUNCTION CONTROL
    def waterSensor(self):
        water = False
        water = True    #<-- change to check soil sensor...
        return water
        
    def waterFall(self, mm): #<-- implement
        return 
        
        
    ##MOVEMENT
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
            
    def move(self, posx, posy, posz, spd):
        """
        posx:Int ,posy:Int ,posz:Int
        spd :Int
        """
        log("going to " + str(posx) + ", " + str(posy) + ", " + str(posz), message_type='debug')
        #send_celery_script(
        self.check_celerypy(cp.move_absolute(location=[posx, posy, posz], offset=[0,0,0], speed=spd))
        #)
    
    def goto(self, x, y, z):
        self.move(self.coords[0], self.coords[1], 0, 100)
        self.move(x, y, 0, 100)
        self.move(x, y, z, 100)
        self.coords = [x, y, z]
    
    def getTool(self, tool):
        l = self.s.toolList[tool]
        self.goto(l[0] , l[1], l[2])
        self.move(l[0] + 100, l[1], l[2], 50)
        self.coords = l
        
    def putTool(self, tool):
        l = self.s.toolList[tool]
        self.goto(l[0] + 100 , l[1], l[2])
        self.move(l[0], l[1], l[2], 50)
        self.move(l[0], l[1], l[2] + 100, 50)
        self.coords = l
        
      
    ##SEQUENCES   
    def water(self):
        whereWater = []
        l = self.s.waterAccessList
        self.getTool("waterSensor")
        for i in l:
            self.goto(i[0], i[1], i[2])
            sensor = waterSensor()
            while sensor == False:
                self.move(i[0], i[1], self.coords[2] - 20, 20)
                self.coords[2] -= 20
            whereWater.append(i[2]-self.coords[2])
        self.putTool("waterSensor")
        self.getTool("water")
        for i in range(len(l)):
            if whereWater[i] > 0:
                self.goto(l[i][0], l[i][1], l[i][2])
                self.waterFall(whereWater[i])
        self.putTool("water")
    
    def repot(self):
        return            
              
                  
    ##START POINT
    def run(self):
        log("Farmware running...", message_type='info')
        self.move(100, 100, -50, 50)
        self.s = Structure()
        log("Data loaded.", message_type='info')
        self.move(150, 150, 0, 50)
        log("Test successful.", message_type='info')
        #self.s.moveRel(100,100,100,50)
        #self.s.calibrate()
        
        ##TESTS
        """
        self.s.sendMail(0)
        #self.s.initFarmLayout()
        #self.s.initPlantTypes()
        print(self.s.currDate())
        print(self.s.currTime())
        #print(list(pot.region.ident for pot in self.s.potList))
        #print(list(self.s.regionList[region].ident for region in self.s.regionList))
        #print(list(pt.name for pt in self.s.plantTypeList))
        print("lol Sylvain") 
        #plant pickle test
        #self.s.plantList.append(Plant("plant1", potList[0].ident))
        #print(list(plant.id for plant in plantList))
        #savePlants()
        print(self.s.plantList, " <-- plantlist")
        print(self.s.waterAccessList, " <-- waterAccessList")
        print(self.s.plantTypeList, " <-- plantTypeList")
        print(self.s.waterList, " <-- waterList")
        print(self.s.repotList, " <-- repotList")
        print(self.s.potList, " <-- potList")
        print(self.s.regionList, " <-- regionList")
        print(self.s.toolList, " <-- toolList")
        #loadPlants()
        #print(list(plant.id for plant in plantList))
        """
        
        ##MAIN WHILE
        while True:
            """
            check timelists for tasks, else wait the remaining time
            """
            break
            currHour = int(self.s.currTime().split(":")[0])
            if (currHour in self.s.waterList) and (self.s.waterList != []):
                self.water()
                self.s.waterList = self.s.waterList[1:]
                
            if (currHour in self.s.repotList) and (self.s.repotList != []):
                self.repot()
                del self.s.repotList[currHour] 
                
            currMin = int(self.s.currTime().split(":")[1])  
            send_celery_script(cp.wait((59 - currMin)*60*1000)) #59 instead of 60 as safety
            
            
        
