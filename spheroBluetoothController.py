'''
THIS SCRIPT DOES NOT WORK IN ITS CURRENT FORM ANYMORE
I partially changed it to work with a switch pro controller before
moving that to its own script.
'''

from multiprocessing import Process, Value
from evdev import InputDevice, categorize, ecodes
import math
from bluepy import btle
  
import sphero_mini
import sys
import time

# address of the ball
MAC_ball = "CE:F0:E9:F4:9F:C3"
# address of the switch pro controller
MAC_pro = "74:F9:CA:4B:21:6C"
# identifier for the bluetooth controller
controllerName = '/dev/input/event0'

controllerStickMinX = 447
controllerStickMaxX = 3363
controllerStickMinY = 13695
controllerStickMaxY = 59380
controllerStickMinRX = 5664
controllerStickMaxRX = 53824
controllerStickMinRY = 12700
controllerStickMaxRY = 57000

def connect():
    print("Connecting...")
    # Connect:
    sphero = sphero_mini.sphero_mini(MAC_ball, verbosity = 1, waitForResponse = False)
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
    
def getSpeed(X, Y, sprinting):
    speed = math.sqrt(X * X + Y * Y) * (2 if sprinting else 1)
    if(speed > 255):
        speed = 255
    return int(speed)

def getAngle(X, Y):
    angle = -math.degrees(math.atan2(Y, X)) + 90
    if(angle < 0):
        angle = angle + 360
    return int(angle)

# Scale raw stick values to be [-128,127]
def scaleLeftStickX(value):
    return max(min(int(((value >> 4) - controllerStickMinX) * 255 / (controllerStickMaxX - controllerStickMinX)), 255), 0) - 128
def scaleLeftStickY(value):
    return max(min(int(255 - (value - controllerStickMinY) * 255 / (controllerStickMaxY - controllerStickMinY)), 255), 0) - 128
def scaleRightStickX(value):
    return max(min(int((value - controllerStickMinRX) * 255 / (controllerStickMaxRX - controllerStickMinRX)), 255), 0) - 128
def scaleRightStickY(value):
    return max(min(int(255 - (value - controllerStickMinRY) * 255 / (controllerStickMaxRY - controllerStickMinRY)), 255), 0) - 128

def MainProgram(currX, currY, currRX, currRY, currRZ):
    sphero = 0
    connected = False
    staring = False # "staring" means the ball is constantly setting its heading to where it's facing
    sprinting = False
    start = time.time()
    
    minX = 1000000000
    maxX = -1000000000
    minRX = 1000000000
    maxRX = -1000000000
    minY = 1000000000
    maxY = -1000000000
    minRY = 1000000000
    maxRY = -1000000000
    mask1s = 0x0000
    mask0s = 0xFFFF
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
    
    pro = switchProController.pro_controller(MAC_pro, "param")
    
    # Loop by reading the controller's input events
    for event in gamepad.read_loop():
        try:
            #print("---")
            #print("Event: %i %i %i" %(event.type, event.code, event.value))
            if(event.type == ecodes.EV_SYN):
                # Process the last changes
                if(time.time() - start > .1):
                    scaledRX = scaleRightStickX(currRX.value)
                    scaledRY = scaleRightStickY(currRY.value)
                    scaledX = scaleLeftStickX(currX.value)
                    scaledY = scaleLeftStickY(currY.value)
                    if(connected):
                        if(staring):
                            sphero.roll(0, getAngle(scaledRX, scaledRY))
                        else:
                            sphero.roll(getSpeed(scaledX, scaledY, sprinting), getAngle(scaledX, scaledY))
                    #print("Left  speed: %i angle: %i" % (getSpeed(scaledX, scaledY, sprinting), getAngle(scaledX, scaledY)))
                    #print("Right speed: %i angle: %i" % (getSpeed(scaledRX, scaledRY, sprinting), getAngle(scaledRX, scaledRY)))
                    start = time.time()
                '''
                if(currX.value < minX):
                    minX = currX.value
                if(currRX.value < minRX):
                    minRX = currRX.value
                if(currY.value < minY):
                    minY = currY.value
                if(currRY.value < minRY):
                    minRY = currRY.value
                    
                if(currX.value > maxX):
                    maxX = currX.value
                if(currRX.value > maxRX):
                    maxRX = currRX.value
                if(currY.value > maxY):
                    maxY = currY.value
                if(currRY.value > maxRY):
                    maxRY = currRY.value
                mask1s = mask1s | currY.value
                mask0s = mask0s & currY.value
                print("mask1s: %s" % (format(mask1s, 'b')))
                print("mask0s: %s" % (format(mask0s, 'b')))
                print("X:  %i" % (currX.value))
                print("Y:  %i" % (currY.value))
                print("RX: %i" % (currRX.value))
                print("RY: %i" % (currRY.value))
                print("minX:  %i" % (minX))
                print("maxX:  %i" % (maxX))
                print("minY:  %i" % (minY))
                print("maxY:  %i" % (maxY))
                print("minRX:  %i" % (minRX))
                print("maxRX:  %i" % (maxRX))
                print("minRY:  %i" % (minRY))
                print("maxRY:  %i" % (maxRY))
                '''
                #print("RZ: %i" % (currRZ.value))
                #plt.show(block=False)
            elif(event.code == ecodes.REL_X):
                #print(event.type, event.code, event.value)
                currX.value = event.value
            elif(event.code == ecodes.REL_Y):
                #print(event.type, event.code, event.value)
                currY.value = event.value
            elif(event.code == ecodes.REL_RX):
                #print(event.type, event.code, event.value)
                currRX.value = event.value
            elif(event.code == ecodes.REL_RY):
                #print(event.type, event.code, event.value)
                currRY.value = event.value
            elif(event.code == ecodes.BTN_TR):
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
            elif(event.code == ecodes.BTN_TR2):
                # Connect
                if(not connected and event.value == 1):
                    sphero = connect()
                    connected = True
                # Disconnect
                elif(connected and event.value == 1):
                    connected = False
                    disconnect(sphero)
            elif(event.code == ecodes.BTN_EAST):
                sprinting = event.value > 0
        except btle.BTLEInternalError:
            print("Lost connection with ball.")
            connected = False

if __name__ == '__main__':
    currX = Value('i', (controllerStickMaxX - controllerStickMinX) // 2 + controllerStickMinX)
    currY = Value('i', (controllerStickMaxY - controllerStickMinY) // 2 + controllerStickMinY)
    currRX = Value('i', (controllerStickMaxRX - controllerStickMinRX) // 2 + controllerStickMinRX)
    currRY = Value('i', (controllerStickMaxRY - controllerStickMinRY) // 2 + controllerStickMinRY)
    currRZ = Value('i', 0)
    
    #p = Process(target = runGraph, args = (currX, currY, currRX, currRY, currRZ)).start()
    MainProgram(currX, currY, currRX, currRY, currRZ)
    #p.join()
