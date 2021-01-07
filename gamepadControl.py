from multiprocessing import Process, Value
from inputs import get_gamepad
from inputs import devices
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')


for device in devices:
    print(device)

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
    
def MainProgram(currX, currY, currRX, currRY, currRZ):
    while 1:
        #print("---")
        events = get_gamepad()
        for event in events:
            #print(event.ev_type, event.code, event.state)
            if(event.code == "ABS_X"):
                currX.value = event.state
            elif(event.code == "ABS_Y"):
                currY.value = -event.state
            if(event.code == "ABS_RX"):
                currRX.value = event.state
            elif(event.code == "ABS_RY"):
                currRY.value = -event.state
            elif(event.code == "ABS_RZ"):
                currRZ.value = event.state
            elif(event.code == "SYN_REPORT"):
                # Process the last changes
                #print("X:  %i" % (currX.value))
                #print("Y:  %i" % (currY.value))
                #print("RX: %i" % (currRX.value))
                #print("RY: %i" % (currRY.value))
                #print("RZ: %i" % (currRZ.value))
                plt.show(block=False)

if __name__ == '__main__':
    currX = Value('i', 0)
    currY = Value('i', 0)
    currRX = Value('i', 0)
    currRY = Value('i', 0)
    currRZ = Value('i', 0)
    
    p = Process(target = runGraph, args = (currX, currY, currRX, currRY, currRZ)).start()
    MainProgram(currX, currY, currRX, currRY, currRZ)
    p.join()