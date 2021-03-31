import qi
import time
import math
import numpy as np
import cv2
import csv
import vision_definitions

class PepperRobot:
    def __init__(self,host="127.0.0.1",port="9559"):
        self.host=host
        self.port=port
        self.session=qi.Session()
        self.memoryProxy=None
        self.motion_service=None
        self.dcm_service=None
        self.videoDevice=None
        self.theta0=0

    def connect(self):
        try:
            self.session.connect("tcp://"+self.host+":"+self.port)
            self.motion_service=self.session.service("ALMotion")
            self.motion_service.setExternalCollisionProtectionEnabled("All", True) #safety for collision
        except Exception as e:
            print(e)
    def disconnect(self):
        self.session.close()
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
    
    def measure_frame_rate(self,width=320,height=240,runtime=60,desired_fps=30):
        self.videoDevice = self.session.service('ALVideoDevice')

        # subscribe top camera
        AL_kTopCamera = 0
        AL_kQVGA = 1            # 320x240
        AL_kBGRColorSpace = 13
        # captureDevice = self.videoDevice.subscribeCamera(
        #     "test3", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 30)
        if(width==320):
            captureDevice = self.videoDevice.subscribe("python_GVM",vision_definitions.kQVGA,vision_definitions.kBGRColorSpace,desired_fps)
        elif(width==640):
            captureDevice = self.videoDevice.subscribe("python_GVM",vision_definitions.kVGA,vision_definitions.kBGRColorSpace,desired_fps)
        
        
        
        prev_frame_time=0
        next_frame_time=0
        fr_array=[]
        start_time=time.time()
        
        while True:

            # get image
            result = self.videoDevice.getImageRemote(captureDevice)
            
            # if result == None:
            #     print 'cannot capture.'
            # elif result[6] == None:
            #     print 'no image data string.'
            # else:

            #     # translate value to mat
            #     # values = map(ord, list(result[6]))
                
            #     values = bytearray(list(result[6]))
            #     # print(len(values))
            #     i = 0
            #     for y in range(0, height):
            #         for x in range(0, width):
            #             image.itemset((y, x, 0), values[i + 0])
            #             image.itemset((y, x, 1), values[i + 1])
            #             image.itemset((y, x, 2), values[i + 2])
            #             i += 3
            if(desired_fps==30):
                time.sleep(0.033)
            elif(desired_fps==20):
                time.sleep(0.05)
                
            end_time=time.time()
            new_frame_time=end_time
            fps=1/(new_frame_time-prev_frame_time)
            prev_frame_time=new_frame_time
            
            print("Current FPS: "+str(fps))
            
            fr_array.append({"elapsed_time": new_frame_time,"frame_rate":fps})
            if(end_time-start_time>=runtime):
                with open("framerate_runtime_"+str(width)+"_"+str(height)+"_"+str(desired_fps)+".csv", "w+") as csvfile:
                    fieldnames=["elapsed_time","frame_rate"]
                    writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
                    writer.writeheader()
                    for item in fr_array:
                        writer.writerow(item)
                break #add save opts
            # exit by [ESC]
            # if cv2.waitKey(33) == 27:
            #     with open("framerate_runtime_"+str(runtime)+".csv", "w+") as csvfile:
            #         fieldnames=["elapsed_time","frame_rate"]
            #         writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
            #         writer.writeheader()
            #         for item in fr_array:
            #             writer.writerow(item)
            #     break #add save opts
def main():
    pepper=PepperRobot()
    pepper.connect()
    pepper.measure_frame_rate(width=320,height=240,desired_fps=30)
    time.sleep(3)
    pepper.measure_frame_rate(width=320,height=240,desired_fps=20)
    time.sleep(3)
    pepper.measure_frame_rate(width=640,height=480,desired_fps=30)
    time.sleep(3)
    pepper.measure_frame_rate(width=640,height=480,desired_fps=20)
    time.sleep(3)

if __name__=="__main__":
    
    main()
       

