from chicken import lights, coop_door, capture_image, temp
import logging

logger=logging.getLogger(__name__)

def main():
    logger.debug("Hello from chickenpi!")
    #capture_image() #ok
    coop_door()     #ok
    #lights()        #ok
    #temp()           #ok

if __name__ == "__main__":
    main()
