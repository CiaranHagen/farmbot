import time, os
import pickle
import xml.etree.ElementTree

##List of functions and classes for ease of use
"""
classes:

PlantType(name, lightNeeded, growthTimeS, growthTimeP, growthTimeF)
Plant(kind, pot)
Pot(region, posx, posy)
Region(ident, gs, position)
___________________________________________________________________

lists:

plantTypeList = plant type repository for accessing data for growth needs
waterList = [time]                --> when to water which pot
repotList = dict[time] = [Plant]  --> when to repot a certain plant
plantList = current plants
potList = a list of pots. This is useful for watering.
regionList = a list of the regions... for specific tasks
___________________________________________________________________

functions:

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
    def __init__(self, ident, region, posx, posy):
        """
        region : Region
        posx : Int
        poxy : Int
        ident : String
        """
        self.region = region
        self.posx = posx
        self.posy = posy
        self.ident = ident
    

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
 
##LIST AND VARIABLE INITIALIZATIONS
plantTypeList = []              #plant type repository for accessing data for growth needs
waterList = []                  #[time]                --> when to water which pot
repotList = {}                  #dict[time] = [Plant]  --> when to repot a certain plant
plantList = []                  #current plants
potList = []                    #a list of pots. This is useful for watering.
regionList = {}                 #a list of the regions... for specific tasks

##TIME AND DATE FUNCTIONS
def currDate():
    """
    return current date as string in dd/mm/yyyy format
    """
    return str(time.localtime(time.time())[2]) + "/" + str(time.localtime(time.time())[1]) + "/" + str(time.localtime(time.time())[0])
def currTime():
    """
    return current time as string in hh:mm format
    """
    return str(time.localtime(time.time())[3]) + ":" + str(time.localtime(time.time())[4])
    
    
    
##UPDATE FUNCTIONS
def uWaterList(step):
    """
    Divide up the day, to water at regular intervals (step).
    """
    for i in range(1, 24):
        if i % step == 0:
            waterList.append(i)
    return
    
    
def checkDead():
    return
    
    
def uRepotList():
    """
    empty old repotList and check each plant for the remaining days, before repot.
    """
    repotList == {}
    for plant in plantList:
        if plant.growthStage == 0:
            remTime = plant.kind.growthTime0 - plant.daysInStage
        elif plant.growthStage == 1:
            remTime = plant.kind.growthTime1 - plant.daysInStage
        elif plant.growthStage == 2:
            remTime = plant.kind.growthTime2 - plant.daysInStage
            
        if remTime in repotList:
            repotList[remTime].append(plant)
    return
    
##INITIALIZATION FUNCTIONS
def initFarmLayout():
    e = xml.etree.ElementTree.parse('./potLayout.xml').getroot()
    
    for region in e:
        #init regions
        x1 = int(region.attrib["x1"])
        x2 = int(region.attrib["x2"])
        y1 = int(region.attrib["y1"])
        y2 = int(region.attrib["y2"])
        gs = int(region.attrib["gs"])
        ident = int(region.attrib["id"])
        
        regionList[region.attrib["id"]] = Region(ident, gs, ((x1, y1), (x2, y2)))
        
        if region.attrib["gs"] == "0":
            #init bacs in region 0
            for bac in region:
                x1 = int(bac.attrib["x1"])
                x2 = int(bac.attrib["x2"])
                y1 = int(bac.attrib["y1"])
                y2 = int(bac.attrib["y2"])
                border = int(bac.attrib["border"])
                dist = int(bac.attrib["dist"])
                
                for i in range(x1 + border, x2 - border + 1, dist):
                    for j in range(y1 + border, y2 - border + 1, dist):
                        pot = Pot(regionList[region.attrib["id"]], i, j)
                        potList.append(pot)
                        
        else:
            #init pots in other regions
            for pot in region:
                pot = Pot(pot.attrib["id"], regionList[region.attrib["id"]], int(pot.attrib["x"]), int(pot.attrib["y"]))
                potList.append(pot)
 

def initPlantTypes():
    e = xml.etree.ElementTree.parse('./plantTypes.xml').getroot()
    for plantType in e:
        name = plantType.attrib["name"]
        lightNeeded = int(plantType.attrib["lightNeeded"])
        gt0 = int(plantType.attrib["gt0"])
        gt1 = int(plantType.attrib["gt1"])        
        gt2 = int(plantType.attrib["gt2"])     
           
        plantTypeList.append(PlantType(name, lightNeeded, gt0, gt1, gt2))
        
def savePlants():
    for plant in plantList:
        f = open("./plants/" + plant.id + ".txt" , "wb")
        pickle.dump(plant, f)
        f.close()
        
def loadPlants():
    for file in os.listdir("./plants"):
        if file.endswith(".txt"):
            f = open("./plants/" + file, "rb")
            plant = pickle.Unpickler(f).load()
            plantList.append(plant)
            f.close()
    
def calibrate():
    return  
    
##SEND MAIL FUNCTION(S)
def sendMail(kind):
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
    """    
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    Fromadd = "XXXXX@gmail.com"
    Toadd = "XXXX@gmail.com"
    cc = ["ad maildest 1","ad mail dest 2"]
    bcc = "ad mail dest 3"
    message = MIMEMultipart() ## création de l'objet "message"
    message['From']= Fromadd
    message['To'] = Toadd
    message['CC']=','.join(cc)
    message['BCC']=bcc
    message['Subject']= "Sujet du mail"
    msg = "Votre message"
    messageattach(MIMEText(msg.encode('utf-8'),'plain','utf-8'))

    serveur = smtplib.SMTP('smtp.gmail.com',587) ## Connexion au serveur sortant (envoie) en précisant son nom et son port
    serveur.starttls() ## Spécification de la sécurisation
    serveur.login(Fromadd,"MDP") ## Authentification
    texte=message.as_string().encode('utf-8')## Conversion de l'objet "message en chaine de caractères et en encodage utf-8
    Toadds=[Toadd]+cc+[bcc] ## Rassemblement des destinataires
    serveur.sendmail(Fromadd,Toadds,texte)
    serveur.quit()
    """
 
    
    
    
##TESTS
sendMail(0)
initFarmLayout()
initPlantTypes()
    
print(currDate())
print(currTime())
print(list(pot.region.ident for pot in potList))
print(list(regionList[region].ident for region in regionList))
print(list(pt.name for pt in plantTypeList))
print("lol Sylvain")    

#plant pickle test
plantList.append(Plant("plant1", potList[0].ident))
print(list(plant.id for plant in plantList))
savePlants()
plantList = []
loadPlants()
print(list(plant.id for plant in plantList))

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
