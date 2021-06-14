import socketio
import time
import random
import sys
import threading
import signal
FACETRACKER=False
sio = socketio.Client()

@sio.event
def connect():
    print('connection established')


@sio.event
def disconnect():
    print('disconnected from server')


@sio.on("TOFACETRACKSTATUS")
def toggleFaceTrack(data):
    if(data == 0):
        FACETRACKER=False
    else:
        FACETRACKER=True


def streamFaceTrackStatus():
    print("Face tracker status started")
    while(True):
        if(FACETRACKER==True):
            sio.emit("FACETRACKSTATUS", 1)
        else:
            sio.emit("FACETRACKSTATUS", 0)
        time.sleep(10)


def streamSonarData():
    print("Sonar streamer started")
    while(True):
        
        front = random.randint(155, 389)/100
        back = random.randint(155, 389)/100
        
        sio.emit("PEPPERSONAR", {"front": front, "back": back})
        time.sleep(2)


def streamBatteryData():
    print("Battery charge streamer started")
    while(True):
        # charge=memory_service.getData("Device/SubDeviceList/Battery/Charge/Sensor/Value")
        battery_charge = 50
        sio.emit("PEPPERBATTERY", battery_charge)
        time.sleep(15)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


sio.connect('http://peppersock.isensetune.com:9543')

# sio.wait()
def main():
    signal.signal(signal.SIGINT, signal_handler)
    try:
        threading.Thread(target=streamBatteryData).start()
        threading.Thread(target=streamSonarData).start()
        threading.Thread(target=streamFaceTrackStatus).start()
    except KeyboardInterrupt:
        sio.disconnect()
        sys.exit(1)


if __name__ == "__main__":
    main()
