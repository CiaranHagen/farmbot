import time, os, json, requests
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
    def __init__(self, name, hole, growthTimeS, growthTimeP, growthTimeF, seedx, seedy, seedz):
        """
        name : string
        lightNeeded : int (lumen)
        waterNeeded : int (ml/day)
        growthTimeS : int (days)
        growthTimeP : int (days)
        growthTimeF : int (days)
        """
        self.hole = hole
        self.name = name
        self.growthTime0 = growthTimeS
        self.growthTime1 = growthTimeP
        self.growthTime2 = growthTimeF
        self.x = seedx
        self.y = seedy
        self.z = seedz
        
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
        self.x = posx
        self.y = posy
        self.z = posz
        
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
    waterAccessList = [[1980,740,-320]]             #[[Int,Int,Int]]       --> water access point coords
    repotList = {}                  #dict[time] = [Plant]  --> when to repot a certain plant
    plantList = []                  #current plants
    potList = []                    #a list of pots. This is useful for watering.
    regionList = {}                 #a list of the regions... for specific tasks
    toolList = {"seeder":[0,0,0], "planter":[0,0,0], "soilSensor":[0,0,0]}

    def __init__(self):
        self.initPlantTypes()
        self.initFarmLayout()
        self.uWaterList(2)
        self.loadPlants()
        self.loadPots()
        self.uRepotList()
        self.initTools()
        
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
                    
                    for i in range(x1 + border, x2 - border, dist):
                        for j in range(y1 + border, y2 - border, dist):
                            pot = Pot(region.attrib["id"] + "," + str(i) + "," + str(j), self.regionList[region.attrib["id"]], i, j, z)
                            self.potList.append(pot)
                            
            else:
                #init pots in other regions
                for pot in region:
                    pot = Pot(pot.attrib["id"], self.regionList[region.attrib["id"]], int(pot.attrib["x"]), int(pot.attrib["y"]), int(pot.attrib["z"]))
                    self.potList.append(pot)
        log("Loaded pot layout.", message_type='info')

    def initPlantTypes(self):
        filer = join(dirname(__file__), 'plantTypes.xml')
        try:
            e = xml.etree.ElementTree.parse(filer).getroot()
        except Exception as error:
            log(repr(error))
        log("Accessed plantTypes.xml", message_type='info')
        for plantType in e:
            name = plantType.attrib["name"]
            if int(plantType.attrib["hole"]) == 1:
                hole = True
            else:
                hole = False
            gt0 = int(plantType.attrib["gt0"])
            gt1 = int(plantType.attrib["gt1"])        
            gt2 = int(plantType.attrib["gt2"]) 
            seedx = int(plantType.attrib["x"])
            seedy = int(plantType.attrib["y"])
            seedz  = int(plantType.attrib["z"])
               
               
            self.plantTypeList.append(PlantType(name, hole, gt0, gt1, gt2, seedx, seedy, seedz))
        log("Loaded plant types.", message_type='info')
           
    def initTools(self):
        filer = join(dirname(__file__), 'tools.xml')
        try:
            e = xml.etree.ElementTree.parse(filer).getroot()
        except Exception as error:
            log(repr(error))
        log("Accessed tools.xml", message_type='info')
        for tool in e:
            ident = tool.attrib["ident"]
            pos = [int(tool.attrib["x"]),int(tool.attrib["y"]),int(tool.attrib["z"])]   
               
            self.toolList[ident] = pos
        log("Loaded plant types.", message_type='info')
        
    def savePlants(self):
        for plant in self.plantList:
            fname = plant.id + ".txt"
            filer = join(dirname(__file__), 'plants', fname)
            f = open(filer, "wb")
            pickle.dump(plant, f)
            f.close()
        log("Saved plant objects.", message_type='info')
            
    def loadPlants(self):
        for file in os.listdir(join(dirname(__file__), 'plants')):
            if file != "save.txt":
                if file.endswith(".txt"):
                    f = open("./plants/" + file, "rb")
                    plant = pickle.Unpickler(f).load()
                    self.plantList.append(plant)
                    f.close()
        log("Loaded plant objects.", message_type='info')
        
    def savePots(self):
        for pot in self.potList:
            fname = pot.ident + ".txt"
            filer = join(dirname(__file__), 'pots', fname)
            f = open(filer, "wb")
            pickle.dump(pot, f)
            f.close()
        log("Saved pot objects.", message_type='info')
            
    def loadPots(self):
        for file in os.listdir(join(dirname(__file__), 'pots')):
            if file != "save.txt":
                if file.endswith(".txt"):
                    f = open("./pots/" + file, "rb")
                    pot = pickle.Unpickler(f).load()
                    self.potList.append(pot)
                    f.close()
        log("Loaded pot objects.", message_type='info')
        
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
    def read(self, pin, mode, label):
        """ pin : int 64 soil sensor
            mode : 0 digital 1 analog
            label : description str
        """
        try:
            info = send(cp.read_pin(number=pin, mode=mode, label = label))
            return info
        except Exception as error:
            log("Read --> " + repr(error))
        
    def reading(self, pin, signal ):
        """
            pin : int pin number
            signal : 1 analog   /   0 digital
        """

        #Sequence reading pin value    
        ss = Sequence("40", "green")
        ss.add(log("Read pin {}.".format(pin), message_type='info'))
        ss.add(self.read(pin, signal,'Soil'))
        ss.add(log("Sensor read.", message_type='info'))
        send(cp.create_node(kind='execute', args=ss.sequence))
       
    def waterSensor(self):
        self.reading(63,0)
        self.waiting(2000)
        self.reading(64,1)
        
        headers = {'Authorization': 'bearer {}'.format(os.environ['FARMWARE_TOKEN']), 'content-type': "application/json"}

        response = requests.get(os.environ['FARMWARE_URL'] + 'api/v1/bot/state', headers=headers)

        bot_state = response.json()
        value = bot_state['pins']['64']['value']
        log(str(value), message_type='info')
        return (value > 400)
   
    def waterFall(self, mm): #<-- implement
        try:
            self.water_on()
            self.waiting(mm*100)
            self.water_off()
        except Exception as error:
            log("Water --> " + repr(error))
    def Write(self, pin, val, m):
        """
           pin : int 10 for vaccum (0 up to 69)
           val : 1 on / 0 off
           m   : 0 digital / 1 analog
        """
        info = send(cp.write_pin(number=pin, value=val , mode=m))
        return info

    def vacuum_on(self):
        on = Sequence("0", "green")
        on.add(log("Vaccum on ", message_type='info'))
        on.add(self.Write(10,1,0))
        send(cp.create_node(kind='execute', args=on.sequence))

    def vacuum_off(self):
        off = Sequence("01", "green")
        off.add(log("Vaccum off ", message_type='info'))
        off.add(self.Write(10,0,0))
        send(cp.create_node(kind='execute', args=off.sequence))    

    def water_on(self):
        won = Sequence("02", "green")
        won.add(self.Write(9,1,0))
        won.add(log("Water on ", message_type='info'))
        send(cp.create_node(kind='execute', args=won.sequence))    

    def water_off(self):
        wof = Sequence("03", "green")
        wof.add(self.Write(9,0,0))
        wof.add(log("Water off ", message_type='info'))
        send(cp.create_node(kind='execute', args=wof.sequence))
        
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
    
    def waiting(self,time):
        try:
            log("Waiting {} ms".format(time), message_type='debug')
            info = send(cp.wait(milliseconds=time))
            return info
        except Exception as error:
            log("Wait --> " + repr(error))
    
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
        self.coords = [l[0] -100, l[1],l[2]]
        return info
        
    def putTool(self, tool):
        l = self.struct.toolList[tool]
        s = Sequence("putTool", "green")
        s.add(self.goto(l[0] - 100 , l[1], l[2]-2))
        s.add(self.move(l[0], l[1], l[2]-2, 50))
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
        whereWater = []
        l = self.struct.waterAccessList
        self.getTool("soilSensor")
        for i in l:
            self.goto(i[0], i[1], i[2]+78)
            sensor = self.waterSensor()
            while sensor == False and self.coords[2] >= -400: #<-- insert proper floor value
                s = Sequence("findWater", "green")
                s.add(self.move(i[0], i[1], self.coords[2] - 10, 20))
                s.add(log("Looking for water.", message_type='info'))
                send(cp.create_node(kind='execute', args=s.sequence)) 
                self.coords[2] -= 10
                sensor = self.waterSensor()
                self.waiting(2000)
            
            whereWater.append(i[2]+78-self.coords[2])
        self.putTool("soilSensor")
        
        for i in range(len(l)):
            if whereWater[i] > 0:
                self.goto(l[i][0], l[i][1], l[i][2])
                self.waterFall(whereWater[i])
    
    def makePlant(self, pot, tplant):
        if pot.plant == None:
            plantTyper = next(y for y in self.struct.plantTypeList if y.name == tplant)
            plant = Plant(plantTyper, pot)
            log("Planting " + tplant + " in pot " + pot.ident, message_type='info')
            pot.plant = plant
            self.struct.plantList.append(plant)
            if plant.kind.hole:
                return None,plant
            else:
                return plant, plant
                
    def plant(self):
        filer = join(dirname(__file__), 'input.txt')
        holeL = []
        plantL = []
        readL = []
        f = open(filer, "rb")
        for line in f:
            line = line.split()
            readL.append((line[0],line[1]))
        f.close()
        
        for p in readL:
            for z in range(int(p[0])):
                potter = next((pot for pot in self.struct.potList if pot.plant == None), None)
                x = self.makePlant(potter, p[1])
                if x[0] != None:
                    holeL.append(x[0])
                plantL.append(x[1])
                
        self.struct.savePlants()
        self.struct.savePots()
        self.getTool("planter")
        for p in holeL:
            self.goto(p.pot.x, p.pot.y, p.pot.z)   
        self.putTool("planter")
        self.getTool("seeder")
        for p in plantL:
            self.goto(p.kind.x, p.kind.y, p.kind.z)
            self.vacuum_on()
            self.goto(p.pot.x, p.pot.y, p.pot.z + 75)
            self.vacuum_off()
        self.putTool("seeder")
        
        f = open(filer, "wb")
        f.close()
        
    def repot(self):
        return            
              
                  
    ##START POINT
    def run(self):
        log("Farmware running...", message_type='info')
        self.struct = Structure()
        log("Data loaded.", message_type='info')
        
        self.goto(0,0,0)
        self.water()
        self.plant()
        
        log("Test successful.", message_type='info')
                
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
        print(self.struct.toolList, " <-- toollist")
        print(self.struct.plantList, " <-- plantlist")
        print(self.struct.waterAccessList, " <-- waterAccessList")
        print(self.struct.plantTypeList, " <-- plantTypeList")
        print(self.struct.waterList, " <-- waterList")
        print(self.struct.repotList, " <-- repotList")
        print(len(self.struct.potList), " <-- potList")
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
            self.waiting((59 - currMin)*60*1000) #59 instead of 60 as safety
            
            
            
            
        
