from multiprocessing import Process, Value
from evdev import InputDevice, categorize, ecodes
import math
  
import sphero_mini
import sys
import time

    
MAC = "CE:F0:E9:F4:9F:C3"
controllerName = '/dev/input/event0'
'''

'''
# Aiming:
#sphero.setLEDColor(red = 0, green = 0, blue = 0) # Turn main LED off
#sphero.stabilization(False) # Turn off stabilization
#sphero.setBackLEDIntensity(255) # turn back LED on
#sphero.wait(3) # Non-blocking pause
#sphero.resetHeading() # Reset heading
#sphero.stabilization(True) # Turn on stabilization
#sphero.setBackLEDIntensity(0) # Turn back LED off

# Move around:
#angle = 0
#angle_increment = 25
#start = time.time()

# Approximate a circle by moving forward in short bursts, then adjusting heading slightly
#while(time.time() - start < 30):
    
#    sphero.setLEDColor(red = 0, green = 0, blue = 255) # Turn main LED blue
#    sphero.roll(100, angle)  # roll forwards (heading = 0) at speed = 50
#
#    sphero.wait(0.5)          # Keep rolling for three seconds
#
#    angle += angle_increment
#    if angle >= 360:
#        angle = 0

#sphero.roll(0, 0)       # stop
#sphero.wait(1)          # Allow time to stop

#sphero.sleep()
#sphero.disconnect()

'''
for device in devices:
    print(device)
'''
'''
def runGraph(currX, currY, currRX, currRY, currRZ):
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    ax1.set_aspect(1)

    def plotInputs(i):
        ax1.clear()
        ax1.plot([0, currX.value], [0, currY.value])
        ax1.plot([0, currRX.value], [0, currRY.value])
        ax1.plot([0, currRZ.value * 128], [0, 0])
        ax1.set_xlim(-40000, 40000)
        ax1.set_ylim(-40000, 40000)
        #print("Showing: %i" % currX.value)
        
    ani = animation.FuncAnimation(fig, plotInputs, interval = 250)
    plt.show()
'''


def connect():
    print("Connecting...")
    # Connect:
    sphero = sphero_mini.sphero_mini(MAC, verbosity = 1, waitForResponse = False)
    sphero.setLEDColor(red = 0, green = 255, blue = 0)
    '''
    # battery voltage
    sphero.getBatteryVoltage()
    print(f"Battery voltage: {sphero.v_batt}v")

    # firmware version number
    sphero.returnMainApplicationVersion()
    print(f"Firmware version: {'.'.join(str(x) for x in sphero.firmware_version)}")
    '''
    sphero.setLEDColor(red = 0, green = 0, blue = 255)
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
    connected = False
    staring = False
    sprinting = False
    start = time.time()
    gamepad = InputDevice(controllerName)
    print(gamepad)
    
    for event in gamepad.read_loop():
        if(event.type == ecodes.EV_SYN):
            # Process the last changes
            if(time.time() - start > .05):
                if(connected):
                    if(staring):
                        sphero.roll(0, getAngle(currRX.value, currRY.value))
                        #print("speed: %i angle: %i" % (0, getAngle(currRX.value, currRY.value)))
                    else:
                        sphero.roll(getSpeed(currX.value, currY.value, sprinting), getAngle(currX.value, currY.value))
                        #print("speed: %i angle: %i" % (getSpeed(currX.value, currY.value, sprinting), getAngle(currX.value, currY.value)))
                
                start = time.time()
        elif(event.code == ecodes.ABS_X):
            currX.value = event.value
        elif(event.code == ecodes.ABS_Y):
            currY.value = -event.value
        elif(event.code == ecodes.ABS_RX):
            currRX.value = event.value
        elif(event.code == ecodes.ABS_RY):
            currRY.value = -event.value
        elif(event.code == ecodes.ABS_RZ):
            currRZ.value = event.value
            if(currRZ.value > 128):
                if(not staring):
                    sphero.setLEDColor(red = 0, green = 0, blue = 0) # Turn main LED off
                    sphero.setBackLEDIntensity(255) # turn back LED on
                    staring = True
            elif(currRZ.value < 64):
                if(staring):
                    sphero.setLEDColor(red = 0, green = 0, blue = 255) # Turn main LED off
                    sphero.setBackLEDIntensity(0) # turn back LED on
                    sphero.resetHeading() # Reset heading
                    staring = False
        elif(event.code == ecodes.BTN_START):
            # Connect
            if(not connected and event.value == 1):
                sphero = connect()
                connected = True
        elif(event.code == ecodes.BTN_SELECT):
            # Disconnect
            if(connected and event.value == 1):
                connected = False
                disconnect(sphero)
        elif(event.code == ecodes.BTN_EAST):
            sprinting = event.value == 1

if __name__ == '__main__':
    currX = Value('i', 0)
    currY = Value('i', 0)
    currRX = Value('i', 0)
    currRY = Value('i', 0)
    currRZ = Value('i', 0)
    
    #p = Process(target = runGraph, args = (currX, currY, currRX, currRY, currRZ)).start()
    MainProgram(currX, currY, currRX, currRY, currRZ)
    #p.join()
