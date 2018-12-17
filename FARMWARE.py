import time, os
import pickle
import xml.etree.ElementTree
from farmware_tools import log
from farmware_tools import send_celery_script as send
import CeleryPy as cp
from os.path import dirname, join

##List of functions and classes for ease of use
"""
SECONDARY FUNCTION CLASSES:

PlantType(name, lightNeeded, growthTimeS, growthTimeP, growthTimeF)
Plant(kind, pot)
Pot(region, posx, posy, posz)
Region(ident, gs, position)
Structure()
___________________________________________________________________

parameter lists of Structure:

plantTypeList = plant type repository for accessing data for growth needs
waterList = [time]                --> when to water which pot
repotList = dict[time] = [Plant]  --> when to repot a certain plant
plantList = current plants
potList = a list of pots. This is useful for watering.
regionList = a list of the regions... for specific tasks
___________________________________________________________________

methods of Structure:

currDate()
currTime()
uWaterList(step) --> step = interval between water checks
uRepotList()
checkDead()
initFarmLayout()
initPlantTypes()
sendMail(kind) --> kind defines which message to send
"""

##CLASSES
class PlantType():
    def __init__(self, name, lightNeeded, growthTimeS, growthTimeP, growthTimeF):
        """
        name : string
        lightNeeded : int (lumen)
        waterNeeded : int (ml/day)
        growthTimeS : int (days)
        growthTimeP : int (days)
        growthTimeF : int (days)
        """
        self.name = name
        self.lightNeeded = lightNeeded
        self.growthTime0 = growthTimeS
        self.growthTime1 = growthTimeP
        self.growthTime2 = growthTimeF
        
class Plant():
    growthStage = 0
    daysInStage = 0
    plantId = 0
    def __init__(self, kind, pot):
        """
        kind : PlantType
        pot : Pot
        """
        self.kind = kind
        self.pot = pot
        self.id = str(Plant.plantId)
        Plant.plantId += 1
    
class Pot():
    """
    plant : Plant
    full : boolean (presence of peat)
    """
    plant = None 
    full = False
    def __init__(self, ident, region, posx, posy, posz):
        """
        region : Region
        posx : Int
        poxy : Int
        ident : String
        """
        self.region = region
        self.ident = ident
        self.point = cp.add_point(posx, posy, posz, 1)
    

class Region():
    def __init__(self, ident, gs, position):
        """
        gs : int
        position : ((<x1>,<y1>),(<x2>,<y2>))
        ident : string
        """
        self.growthStage = gs
        self.position = position
        self.ident = ident


class Structure():
 
    ##LIST AND VARIABLE INITIALIZATIONS
    plantTypeList = []              #plant type repository for accessing data for growth needs
    waterList = []                  #[time]                --> when to water
    waterAccessList = []             #[[Int,Int,Int]]       --> water access point coords
    repotList = {}                  #dict[time] = [Plant]  --> when to repot a certain plant
    plantList = []                  #current plants
    potList = []                    #a list of pots. This is useful for watering.
    regionList = {}                 #a list of the regions... for specific tasks
    toolList = {"water":[2676,871,-368], "seeder":[0,0,0], "holer":[2676,871,-368], "waterSensor":[0,0,0]}

    def __init__(self):
        log("Init - 0 --> structure", message_type='info')
        self.initPlantTypes()
        log("Init - 1 --> structure", message_type='info')
        self.initFarmLayout()
        log("Init - 2 --> structure", message_type='info')
        self.uWaterList(2)
        log("Init - 3 --> structure", message_type='info')
        self.loadPlants()
        log("Init - 4 --> structure", message_type='info')
        self.uRepotList()
        log("Init - 5 --> structure", message_type='info')
        
    ##TIME AND DATE FUNCTIONS
    def currDate(self):
        """
        return current date as string in dd/mm/yyyy format
        """
        return str(time.localtime(time.time())[2]) + "/" + str(time.localtime(time.time())[1]) + "/" + str(time.localtime(time.time())[0])
        
    def currTime(self):
        """
        return current time as string in hh:mm format
        """
        return str(time.localtime(time.time())[3]) + ":" + str(time.localtime(time.time())[4]) 
        
    ##UPDATE FUNCTIONS
    def uWaterList(self, step):
        """
        Divide up the day, to water at regular intervals (step).
        """
        for i in range(0, 24):
            if i % step == 0:
                self.waterList.append(i)
        return
        
        
    def uRepotList(self):
        """
        empty old repotList and check each plant for the remaining days, before repot.
        """
        self.repotList == {}
        for plant in self.plantList:
            if plant.growthStage == 0:
                remTime = plant.kind.growthTime0 - plant.daysInStage
            elif plant.growthStage == 1:
                remTime = plant.kind.growthTime1 - plant.daysInStage
            elif plant.growthStage == 2:
                remTime = plant.kind.growthTime2 - plant.daysInStage
                
            if remTime in self.repotList:
                self.repotList[remTime].append(plant)
        return
        
    ##INITIALIZATION FUNCTIONS
    def initFarmLayout(self):
        filer = join(dirname(__file__), 'potLayout.xml')
        e = xml.etree.ElementTree.parse(filer).getroot()
        log("Accessed potLayout.xml", message_type='struct')
        for region in e:
            #init regions
            x1 = int(region.attrib["x1"])
            x2 = int(region.attrib["x2"])
            y1 = int(region.attrib["y1"])
            y2 = int(region.attrib["y2"])
            gs = int(region.attrib["gs"])
            ident = int(region.attrib["id"])
            
            self.regionList[region.attrib["id"]] = Region(ident, gs, ((x1, y1), (x2, y2)))
            
            if region.attrib["gs"] == "0":
                #init bacs in region 0
                for bac in region:
                    x1 = int(bac.attrib["x1"])
                    x2 = int(bac.attrib["x2"])
                    y1 = int(bac.attrib["y1"])
                    y2 = int(bac.attrib["y2"])
                    z = int(bac.attrib["z"])
                    border = int(bac.attrib["border"])
                    dist = int(bac.attrib["dist"])
                    
                    for i in range(x1 + border, x2 - border + 1, dist):
                        for j in range(y1 + border, y2 - border + 1, dist):
                            pot = Pot(self.regionList[region.attrib["id"]], i, j, z)
                            self.potList.append(pot)
                            
            else:
                #init pots in other regions
                for pot in region:
                    pot = Pot(pot.attrib["id"], self.regionList[region.attrib["id"]], int(pot.attrib["x"]), int(pot.attrib["y"]), int(pot.attrib["z"]))
                    self.potList.append(pot)
        log("Loaded pot layout.", message_type='info')

    def initPlantTypes(self):
        filer = join(dirname(__file__), 'plantTypes.xml')
        log("Present.", message_type='info')
        try:
            e = xml.etree.ElementTree.parse(filer).getroot()
        except Exception as error:
            log(repr(error))
        log("Accessed plantTypes.xml", message_type='info')
        for plantType in e:
            name = plantType.attrib["name"]
            lightNeeded = int(plantType.attrib["lightNeeded"])
            gt0 = int(plantType.attrib["gt0"])
            gt1 = int(plantType.attrib["gt1"])        
            gt2 = int(plantType.attrib["gt2"])     
               
            self.plantTypeList.append(PlantType(name, lightNeeded, gt0, gt1, gt2))
        log("Loaded plant types.", message_type='info')
           
    def savePlants(self):
        log("Saving plant objects.", message_type='info')
        for plant in self.plantList:
            fname = plant.id + ".txt"
            filer = join(dirname(__file__), 'plants', fname)
            f = open(filer, "wb")
            pickle.dump(plant, f)
            f.close()
        log("Saved plant objects.", message_type='info')
            
    def loadPlants(self):
        log("Loading plant objects.", message_type='info')
        for file in os.listdir(join(dirname(__file__), 'plants')):
            if file != "save.txt":
                if file.endswith(".txt"):
                    f = open("./plants/" + file, "rb")
                    plant = pickle.Unpickler(f).load()
                    self.plantList.append(plant)
                    f.close()
        log("Loaded plant objects.", message_type='info')
        
    ##SEND MAIL FUNCTION(S)
    def sendMail(self, kind):
        """
        Send a mail to the agriculturist, informing hime of 
            0 : Plants that are ready to be moved
            1 : Empty pot spots
            2 : ...
            
            else : an error
        """
        me = "email"
        you = "me"
        if kind == 0:
            textfile = "./plantsDonemsg.txt"
            subject = "There are plants done."
        elif kind == 1:
            textfile = "./needPeatmsg.txt"
            subject = "Some pots need new peat."
        else:
            textfile = "./errormsg.txt"
            subject = "An error occurred."
            
class Sequence:
    def __init__(self, name='New Sequence', color='gray'):
        self.sequence = {
            'name': name,
            'color': color,
            'body': []
            }
        self.add = self.sequence['body'].append

    
##=================================================================##
##===                MAIN PART OF THE PROGRAM                   ===##
##=================================================================##
    
class MyFarmware():  
    coords = [0,0,0]
    TOKEN = ''
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
    def moveRel(self, distx, disty, distz, spd):
        """
        distx:Int ,disty:Int ,distz:Int
        spd :Int
        """
        log("moving " + str(distx) + ", " + str(disty) + ", " + str(distz), message_type='debug')
        info = send(cp.move_relative(distance=(distx, disty, distz), speed=spd))
        return info
             
    def move(self, posx, posy, posz, spd):
        """
        posx:Int ,posy:Int ,posz:Int
        spd :Int
        """
        log("going to " + str(posx) + ", " + str(posy) + ", " + str(posz), message_type='debug')
        info = send(cp.move_absolute(location=[posx, posy, posz], offset=[0,0,0], speed=spd))
        return info
    
    def goto(self, x, y, z):
        s = Sequence("goto", "green")
        s.add(self.move(self.coords[0], self.coords[1], 0, 100))
        s.add(self.move(x, y, 0, 100))
        s.add(self.move(x, y, z, 100))
        s.add(log("Moved to "+str(x)+", "+str(y)+", "+str(z)+".", message_type='info'))
        info = send(cp.create_node(kind='execute', args=s.sequence)) 
        self.coords = [x, y, z]
        return info
    
    def getTool(self, tool):
        l = self.struct.toolList[tool]
        s = Sequence("getTool", "green")
        s.add(self.goto(l[0] , l[1], l[2]))
        s.add(self.move(l[0] - 100, l[1], l[2], 50))
        s.add(log("Getting "+tool+".", message_type='info'))
        info = send(cp.create_node(kind='execute', args=s.sequence)) 
        self.coords = l
        return info
        
    def putTool(self, tool):
        l = self.struct.toolList[tool]
        s = Sequence("putTool", "green")
        s.add(self.goto(l[0] - 100 , l[1], l[2]))
        s.add(self.move(l[0], l[1], l[2], 50))
        s.add(self.move(l[0], l[1], l[2] + 100, 50))
        s.add(log("Putting back "+tool+".", message_type='info'))
        send(cp.create_node(kind='execute', args=s.sequence)) 
        self.coords = l
        
    def calibrate(self):
        i = 0
        while True and i<21:
            try:
                s = Sequence("xCalib", "green")
                s.add(self.moveRel(-100,0,0,50))
                s.add(log("Calibrating  x axis.", message_type='info'))
                send(cp.create_node(kind='execute', args=s.sequence)) 
                i += 1
            except:
                break
        
        i = 0
        while True and i<14:
            try:
                s = Sequence("yCalib", "green")
                s.add(self.moveRel(0,-100,0,50))
                s.add(log("Calibrating  y axis.", message_type='info'))
                send(cp.create_node(kind='execute', args=s.sequence)) 
                i += 1
            except:
                break
        
        i = 0
        while True and i<4:
            try:
                s = Sequence("zCalib", "green")
                s.add(self.moveRel(0,0,100,50))
                s.add(log("Calibrating  z axis.", message_type='info'))
                send(cp.create_node(kind='execute', args=s.sequence)) 
                i += 1
            except:
                break
              
    ##SEQUENCES   
    def water(self):
        """
        whereWater = []
        l = self.struct.waterAccessList
        self.getTool("waterSensor")
        for i in l:
            self.goto(i[0], i[1], i[2])
            sensor = waterSensor()
            while sensor == False and self.coords[2] >= -100: #<-- insert proper floor value
                s = Sequence("findWater", "green")
                s.add(self.move(i[0], i[1], self.coords[2] - 20, 20))
                s.add(log("Looking for water.", message_type='info'))
                send(cp.create_node(kind='execute', args=s.sequence)) 
                self.coords[2] -= 20
            whereWater.append(i[2]-self.coords[2])
        self.putTool("waterSensor")
        """
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
        
        self.goto(100,100,-50)
        
        log("Move-test finished.", message_type='info')
        
        self.struct = Structure()
        log("Data loaded.", message_type='info')
        
        self.water()
        
        self.calibrate()
        
        log("Test successful.", message_type='info')
        print(self.coords)
        
        ##TESTS
        
        #self.s.sendMail(0)
        #self.s.initFarmLayout()
        #self.s.initPlantTypes()
        #print(struct.currDate())
        #print(struct.currTime())
        #print(list(pot.region.ident for pot in self.s.potList))
        #print(list(self.s.regionList[region].ident for region in self.s.regionList))
        #print(list(pt.name for pt in self.s.plantTypeList))
        #print("lol Sylvain") 
        #plant pickle test
        #self.s.plantList.append(Plant("plant1", potList[0].ident))
        #print(list(plant.id for plant in plantList))
        #savePlants()
        """
        print(self.struct.plantList, " <-- plantlist")
        print(self.struct.waterAccessList, " <-- waterAccessList")
        print(self.struct.plantTypeList, " <-- plantTypeList")
        print(self.struct.waterList, " <-- waterList")
        print(self.struct.repotList, " <-- repotList")
        print(self.struct.potList, " <-- potList")
        print(self.struct.regionList, " <-- regionList")
        print(self.struct.toolList, " <-- toolList")
        """
        #loadPlants()
        #print(list(plant.id for plant in plantList))
        
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
            send(cp.wait((59 - currMin)*60*1000)) #59 instead of 60 as safety
            
            
            
            
        
