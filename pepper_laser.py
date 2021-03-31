import qi
import time
import math


class PepperRobot:
    def __init__(self,host="127.0.0.1",port="9559"):
        self.host=host
        self.port=port
        self.session=qi.Session()
        self.memoryProxy=None
        self.motion_service=None
        self.dcm_service=None
        self.theta0=0

    def connect(self):
        try:
            self.session.connect("tcp://"+self.host+":"+self.port)
            self.motion_service=self.session.service("ALMotion")
            self.motion_service.setExternalCollisionProtectionEnabled("All", True) #safety for collision
        except Exception as e:
            print(e)
    def start_motion_service(self):
        self.motion_service=self.session.service("ALMotion")
        self.theta0 = self.motion_service.getRobotPosition(False)[2]    
    def start_sensor_service(self,serviceName=""):
        if not(self.session.isConnected()):
            return "Connection error"
        try:
            if(serviceName=="memoryProxy"):
                self.memoryProxy=self.session.service("ALMemory")
            
            elif(serviceName=="dcm_service"):
                self.dcm_service=self.session.service("DCM") #DCM (Device Communication Manager)
                t = self.dcm_service.getTime(0)
                self.dcm_service.set(["Device/SubDeviceList/Platform/LaserSensor/Front/Reg/OperationMode/Actuator/Value", "Merge", [[1.0, t]]])
                self.dcm_service.set(["Device/SubDeviceList/Platform/LaserSensor/Right/Reg/OperationMode/Actuator/Value", "Merge", [[1.0, t]]])
                self.dcm_service.set(["Device/SubDeviceList/Platform/LaserSensor/Left/Reg/OperationMode/Actuator/Value", "Merge", [[1.0, t]]])
            # self.motion_service=self.session.service("ALMotion")
            # self.dcm_service=self.session.service("DCM") #DCM (Device Communication Manager)
            return "Success"
        except Exception as e:
            print("line 43")
            return e

    def get_laser_data(self):
        # if self.memoryProxy.getData("MONITOR_RUN")>0:
        theta = self.motion_service.getRobotPosition(False)[2] -self.theta0 + 1.57
        for i in range(0,15):
            if i+1<10:
                stringIndex = "0" + str(i+1)
            else:
                stringIndex = str(i+1)

            y_value = self.memoryProxy.getData("Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg"+stringIndex+"/X/Sensor/Value")# - 0.0562
            x_value = -self.memoryProxy.getData("Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg"+stringIndex+"/Y/Sensor/Value")

            return {'theta':theta+(0.523599-i*0.0698132),'distance':math.sqrt(x_value*x_value + y_value*y_value)}
        
