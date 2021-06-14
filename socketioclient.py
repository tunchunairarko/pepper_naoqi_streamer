import socketio
import time
import qi
import argparse
import sys
import threading
import signal
sio = socketio.Client()


session = qi.Session()
pepper_ip = "127.0.0.1"
pepper_port = 9559
try:
    session.connect("tcp://" + pepper_ip + ":" + str(pepper_port))
except RuntimeError:
    print("Can't connect to Naoqi at ip \"" + pepper_ip + "\" on port " + str(pepper_port) + ".\n"
      "Please check your script arguments. Run with -h option for help.")
    sys.exit(1)
FACETRACKER = session.service("ALFaceDetection")
FACETRACKER.enableTracking(False)
memory_service = session.service("ALMemory")
sonar_service = session.service("ALSonar")
battery_service = session.service("ALBattery")
battery_service.enablePowerMonitoring(True)
motion_service = session.service("ALMotion")


# Example showing how to activate "Move", "LArm" and "RArm" external anti collision
name = "All"
enable = True
motion_service.setExternalCollisionProtectionEnabled(name, enable)


@sio.event
def connect():
    print('connection established')


@sio.event
def disconnect():
    print('disconnected from server')


@sio.on("TOFACETRACKSTATUS")
def toggleFaceTrack(data):
    if(data == 0):
        FACETRACKER.enableTracking(False)
    else:
        FACETRACKER.enableTracking(True)


def streamFaceTrackStatus():
    print("Face tracker status started")
    while(True):
        if(FACETRACKER.isTrackingEnabled()):
            sio.emit("FACETRACKSTATUS", 1)
        else:
            sio.emit("FACETRACKSTATUS", 0)
            time.sleep(10)


def streamSonarData():
    print("Sonar streamer started")
    while(True):
        sonar_service.subscribe("hwuTelecare")
        front = memory_service.getData("Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value")
        back = memory_service.getData("Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value")
        sonar_service.unsubscribe("hwuTelecare")
        sio.emit("PEPPERSONAR", {"front": front, "back": back})
        time.sleep(2)


def streamBatteryData():
    print("Battery charge streamer started")
    while(True):
        # charge=memory_service.getData("Device/SubDeviceList/Battery/Charge/Sensor/Value")
        battery_charge = battery_service.getBatteryCharge()
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
