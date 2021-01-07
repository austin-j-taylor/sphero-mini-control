from multiprocessing import Process, Value
from evdev import InputDevice, categorize, ecodes
import math
  
import sphero_mini
import sys
import time

# address of the ball
MAC = "CE:F0:E9:F4:9F:C3"
# identifier for the bluetooth controller
controllerName = '/dev/input/event2'

def connect():
    print("Connecting...")
    # Connect:
    sphero = sphero_mini.sphero_mini(MAC, verbosity = 1, waitForResponse = False)
    sphero.setLEDColor(red = 255, green = 255, blue = 255)
    sphero.resetHeading() # Reset heading
    print("Connected.")
    return sphero
    
def disconnect(sphero):
    print("Disconnecting...")
    sphero.setLEDColor(red = 255, green = 0, blue = 0)
    sphero.resetHeading() # Reset heading
    sphero.roll(0,0)
    sphero.sleep()
    sphero.setLEDColor(red = 0, green = 0, blue = 0)
    sphero.disconnect()
    print("Disconnected.")
    
def getSpeed(currX, currY, sprinting):
    speed = math.sqrt(currX * currX + currY * currY) * (255 if sprinting else 128) / 32767
    if(speed > 255):
        speed = 255
    return int(speed)

def getAngle(currX, currY):
    angle = -math.degrees(math.atan2(currY, currX)) + 90
    if(angle < 0):
        angle = angle + 360
    return int(angle)

def MainProgram(currX, currY, currRX, currRY, currRZ):
    sphero = 0
    connected = False
    staring = False # "staring" means the ball is constantly setting its heading to where it's facing
    sprinting = False
    start = time.time()
    
    # Attempt to connect to the controller
    while(1):
        try:
            gamepad = InputDevice(controllerName)
            break;
        except FileNotFoundError:
            pass
            print("No device found...")
            time.sleep(1)
    
    print(gamepad)
    
    # Loop by reading the controller's input events
    for event in gamepad.read_loop():
        try:
            #print("---")
            #print("Event: %i %i %i" %(event.type, event.code, event.value))
            if(event.type == ecodes.EV_SYN):
                # Process the last changes
                if(time.time() - start > .1):
                    if(connected):
                        if(staring):
                            sphero.roll(0, getAngle(currRX.value, currRY.value))
                        else:
                            sphero.roll(getSpeed(currX.value, currY.value, sprinting), getAngle(currX.value, currY.value))
                    print("speed: %i angle: %i" % (getSpeed(currX.value, currY.value, sprinting), getAngle(currX.value, currY.value)))
                    start = time.time()
                
                #print("X:  %i" % (currX.value))
                #print("Y:  %i" % (currY.value))
                #print("RX: %i" % (currRX.value))
                #print("RY: %i" % (currRY.value))
                #print("RZ: %i" % (currRZ.value))
                #plt.show(block=False)
            elif(event.code == ecodes.REL_X):
                #print(event.type, event.code, event.value)
                currX.value = int(event.value * 1565.29167)
                currRX.value = int(event.value * 1565.29167)
            elif(event.code == ecodes.REL_Y):
                #print(event.type, event.code, event.value)
                currY.value = int(-event.value * 1565.29167)
                currRY.value = int(-event.value * 1565.29167)
            elif(event.code == ecodes.BTN_LEFT):
                currRZ.value = event.value
                if(currRZ.value > 0):
                    if(not staring and sphero != 0):
                        sphero.setLEDColor(red = 0, green = 0, blue = 0) # Turn main LED off
                        sphero.setBackLEDIntensity(255) # turn back LED on
                        staring = True
                elif(currRZ.value < 1):
                    if(staring and sphero != 0):
                        sphero.setLEDColor(red = 0, green = 0, blue = 255) # Turn main LED off
                        sphero.setBackLEDIntensity(0) # turn back LED on
                        sphero.resetHeading() # Reset heading
                        staring = False
            elif(event.code == ecodes.BTN_RIGHT):
                # Connect
                if(not connected and event.value == 1):
                    sphero = connect()
                    connected = True
                # Disconnect
                elif(connected and event.value == 1):
                    connected = False
                    disconnect(sphero)
            elif(event.code == ecodes.BTN_EAST):
                sprinting = event.value == 1
        except:
            print("Lost connection with ball.")
            connected = False

if __name__ == '__main__':
    currX = Value('i', 0)
    currY = Value('i', 0)
    currRX = Value('i', 0)
    currRY = Value('i', 0)
    currRZ = Value('i', 0)
    
    #p = Process(target = runGraph, args = (currX, currY, currRX, currRY, currRZ)).start()
    MainProgram(currX, currY, currRX, currRY, currRZ)
    #p.join()
