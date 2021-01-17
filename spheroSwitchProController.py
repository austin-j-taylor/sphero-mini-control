from evdev import InputDevice, categorize, ecodes
  
import sphero_mini
import sys
import time
from pyjoycon import PythonicJoyCon, get_PRO_id
import time, math, atexit
from bluepy import btle
    
# address of the ball
MAC_ball = "CE:F0:E9:F4:9F:C3"

# time to sleep between commands to make sure they're not skipped
deltaTime = 1.0/30
deltaTimeLong = deltaTime  *6
# joystick deadband
deadband = 15

controllerStickMinX = 485
controllerStickMaxX = 3463
controllerStickMinY = 412
controllerStickMaxY = 3491
controllerStickMinRX = 340
controllerStickMaxRX = 3370
controllerStickMinRY = 595
controllerStickMaxRY = 3560

# Global so we can turn off lights in our exit callback
joycon = 0
sphero = 0

# Switch Pro Controller functions

def set_home_light(joycon, brightness):
    intensity = 0
    if brightness > 0:
        if brightness < 65:
            intensity = (brightness + 5) // 10
        else:
            intensity = math.ceil(0xF * ((brightness / 100) ** 2.13))
    intensity = (intensity & 0xF) << 4
    param = ((0x01 << 24) | (intensity << 16) | (intensity << 8) | (0x00 << 0)).to_bytes(4, byteorder='big')
    
    joycon._write_output_report(
         b'\x01', b'\x38', param
    )

def exit_handler():
    disconnect()
    disconnectController()

def disconnectController():
    global joycon
    if(joycon != 0):
        joycon.disconnect_device()
        #set_home_light(joycon, 0)
        #time.sleep(deltaTimeLong)
        #joycon.set_player_lamp_flashing(0x8)
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
    ret = max(min(int((value - controllerStickMinX) * 255 / (controllerStickMaxX - controllerStickMinX)), 255), 0) - 128
    if(ret < deadband and ret > -deadband):
        ret = 0
    return ret
def scaleLeftStickY(value):
    ret = max(min(int((value - controllerStickMinY) * 255 / (controllerStickMaxY - controllerStickMinY)), 255), 0) - 128
    if(ret < deadband and ret > -deadband):
        ret = 0
    return ret
def scaleRightStickX(value):
    ret = max(min(int((value - controllerStickMinRX) * 255 / (controllerStickMaxRX - controllerStickMinRX)), 255), 0) - 128
    if(ret < deadband and ret > -deadband):
        ret = 0
    return ret
def scaleRightStickY(value):
    ret = max(min(int((value - controllerStickMinRY) * 255 / (controllerStickMaxRY - controllerStickMinRY)), 255), 0) - 128
    if(ret < deadband and ret > -deadband):
        ret = 0
    return ret

# Sphero functions
def connect():
    global sphero
    print("Connecting...")
    sphero = sphero_mini.sphero_mini(MAC_ball, verbosity = 1, waitForResponse = False)
    sphero.setLEDColor(red = 255, green = 255, blue = 255)
    sphero.resetHeading() # Reset heading
    print("Connected.")
    
def disconnect():
    global sphero
    if(sphero != 0):
        print("Disconnecting from ball...")
        sphero.setLEDColor(red = 255, green = 0, blue = 0)
        sphero.resetHeading() # Reset heading
        sphero.roll(0,0)
        sphero.sleep()
        sphero.setLEDColor(red = 0, green = 0, blue = 0)
        sphero.disconnect()
        print("Disconnected from ball.")
        sphero = 0


def MainProgram():
    connected = False
    staring = False # "staring" means the ball is constantly setting its heading to where it's facing
    sprinting = False
    lastHeading = 90
    start = time.time()
    global sphero, joycon
    
    # Attempt to connect to the controller
    joycon_id = get_PRO_id()
    joycon = PythonicJoyCon(*joycon_id)

    atexit.register(exit_handler)

    print("Pro Controller found: %s" % (joycon_id,))
    time.sleep(deltaTimeLong)
    joycon.set_player_lamp_on(0x1)
    time.sleep(deltaTimeLong)
    print("Battery: %i" % joycon.battery_level)
    if(joycon.battery_level == 0):
        joycon.set_player_lamp_on(0x8)
        exit(1)
        
    set_home_light(joycon, 20)
        
        
        
    while 1:
        time.sleep(deltaTime)
        
        try:
            # End
            if(joycon.minus):
                exit(0)
            if(joycon.plus):
                exit(1)
            # Sprinting, staring states
            sprinting = joycon.a
            if(connected):
                if(staring):
                    if(not joycon.zr):
                        sphero.setLEDColor(red = 255, green = 255, blue = 255)
                        sphero.setBackLEDIntensity(0)
                        sphero.resetHeading() # Reset heading
                        staring = False
                else:
                    if(joycon.zr):
                        sphero.setLEDColor(red = 0, green = 0, blue = 0) # Turn main LED off
                        sphero.setBackLEDIntensity(255) # turn back LED on
                        staring = True
                        
                        
            # Stick positions
            scaledX = scaleLeftStickX(joycon.stick_l[0])
            scaledY = scaleLeftStickY(joycon.stick_l[1])
            scaledRX = scaleRightStickX(joycon.stick_r[0])
            scaledRY = scaleRightStickY(joycon.stick_r[1])
            
            #print("Left  speed: %i angle: %i" % (getSpeed(scaledX, scaledY, sprinting), getAngle(scaledX, scaledY)))
            #print("Right speed: %i angle: %i" % (getSpeed(scaledRX, scaledRY, sprinting), getAngle(scaledRX, scaledRY)))
            # Connected status
            if(connected):
                if(joycon.home):
                    set_home_light(joycon, 5)
                    time.sleep(deltaTimeLong)
                    joycon.set_player_lamp_flashing(0x3)
                    disconnect() 
                    set_home_light(joycon, 20)
                    time.sleep(deltaTimeLong)
                    joycon.set_player_lamp_on(0x1)
                    connected = False
                else:
                    # Don't send roll commands too often
                    if(time.time() - start > .1):
                        start = time.time()
                        if(staring):
                            if(scaledRX != 0 or scaledRY != 0):
                                lastHeading = getAngle(scaledRX, scaledRY)
                            sphero.roll(0, lastHeading)
                        else:
                            if(scaledX != 0 or scaledY != 0):
                                lastHeading = getAngle(scaledX, scaledY)
                            sphero.roll(getSpeed(scaledX, scaledY, sprinting), lastHeading)
            else:
                if(joycon.home):
                    set_home_light(joycon, 5)
                    time.sleep(deltaTimeLong)
                    joycon.set_player_lamp_flashing(0x3)
                    connect()  
                    set_home_light(joycon, 100)
                    time.sleep(deltaTimeLong)
                    joycon.set_player_lamp_on(0x3)
                    connected = True
        except btle.BTLEInternalError:
            print("Lost connection with ball.")
            connected = False
            sphero = 0
    

if __name__ == '__main__':
    
    MainProgram()
