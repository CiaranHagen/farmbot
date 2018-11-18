import time

##CLASSES

class PlantType():
    def __init__(self, name, lightNeeded, waterNeeded, growthTimeS, growthTimeP, growthTimeF):
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
        self.waterNeeded = waterNeeded
        self.growthTimeS = growthTimeS
        self.growthTimeP = growthTimeP
        self.growthTimeF = growthTimeF
        
class Plant():
    growthStage = 0
    daysInStage = 0
    def __init__(self, kind, pot):
        """
        kind : PlantType
        pot : Pot
        """
        self.kind = kind
        self.pot = pot
    
class Pot():
    plant = None 
    full = False
    def __init__(self, region, posx, posy):
        """
        region : Region
        """
        self.region = region
        self.posx = posx
        self.posy = posy
    

class Region():
    def __init__(self, gs, position):
        """
        gs : int
        position : ((<x1>,<y1>),(<x2>,<y2>))
        """
        self.growthStage = gs
        self.position = position
 
##LIST AND VARIABLE INITIALIZATIONS
PlantTypeList = [PlantType]     #plant type repository for accessing data for growth needs
WaterList = {}                  #dict[time] = [Plant]  --> when to water which pot
repotList = {}                  #dict[time] = [Plant]  --> when to repot a certain plant
plantList = [Plant]             #current plants
potList = [Pot]
regionList = [Region]

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
def UWaterList():
    return
def checkDead():
    return
def URepotList():
    return
    
##INITIALIZATION FUNCTIONS
def getPots():
    f = open("./potlayout.txt", "r")
    for line in f:
        line = line.split()
        region = regionList[int(line[0])]
        pot = Pot(region, line[1], line[2])
        potList.append(pot)
    f.close()
    
def initRegions():
    regionList.append(Region(0, ((0,0),(600,600))))         #Need to change all these coords
    regionList.append(Region(1, ((600,0),(1200,600))))
    regionList.append(Region(2, ((1200,0),(1800,600))))
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

    # Import the email modules we'll need
    from email.mime.text import MIMEText

    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    with open(textfile, 'rb') as fp:
        # Create a text/plain message
        msg = MIMEText(fp.read())

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = '%s' % subject
    msg['From'] = me
    msg['To'] = you

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()
"""  
    
sendMail(0)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
