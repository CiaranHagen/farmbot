import os
from FARMWARE import MyFarmware
from farmware_tools import log
import sys


FARMWARE_NAME = "jhempbot"

def get_env(key, type_=str):
    return type_(os.environ["{}_{}".format(farmware_name, key)])

def main():
    log("jhempbot --> hello")
    farmware = MyFarmware(FARMWARE_NAME)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(e ,message_type='error', title=FARMWARE_NAME + " : run" )
        raise Exception(e)


"""

if __name__ == "__main__":

    FARMWARE_NAME = "jhempbot"
    #FARMWARE_NAME = ((__file__.split(os.sep))[len(__file__.split(os.sep))-3]).replace('-master','')

    log('Starting farmware...', message_type='info', title=FARMWARE_NAME)
    
    try:
        reload(sys)
        sys.setdefaultencoding('utf8') #force utf8 for celerypy return code
        log('Setting encoding.', message_type='info', title=FARMWARE_NAME)
    except:
        pass

    try:
        farmware = MyFarmware(FARMWARE_NAME)
        #log('initializing farmware', message_type='info', title=FARMWARE_NAME)
    except Exception as e:
        log(e ,message_type='error', title=FARMWARE_NAME + " : init" )
        raise Exception(e) #Envoyer un message d'erreur -> arrète le programme
    else:
        try:
            #log('farmware runs after this message.', message_type='info', title=FARMWARE_NAME)
            farmware.run()
        except Exception as e:
            log(e ,message_type='error', title=FARMWARE_NAME + " : run" )
            raise Exception(e)


    log('Ending farmware...', message_type='info', title=FARMWARE_NAME)
"""
