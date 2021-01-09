
from pyjoycon import PythonicJoyCon, get_PRO_id
import time, math, atexit
    
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
    print("set home lamp")

def exit_handler():
    disconnect()

def disconnect():
    #joycon.disconnect_device()
    print("Disconnected.")

deltaTime = 1.0/30
joycon_id = get_PRO_id()
joycon = PythonicJoyCon(*joycon_id)

atexit.register(exit_handler)

print(joycon_id)
time.sleep(deltaTime)
joycon.set_player_lamp_on(0x1)
print("set lamp on")
time.sleep(deltaTime * 5)
set_home_light(joycon, 50)
time.sleep(deltaTime)

while 1:
    time.sleep(deltaTime)
    
    print("Left stick:  %s\nRight stick: %s" % (joycon.stick_l, joycon.stick_r))
    
    
    
    '''
    for event_type, status in joycon.events():
        print(event_type, status)
        if(event_type == 'a'):
            set_home_light(joycon, 100 * status)
        elif(event_type == 'y'):
            joycon.set_player_lamp_on(0x2)
            exit()
    '''
