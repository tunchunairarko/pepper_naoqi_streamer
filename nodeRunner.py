from pepper_laser import PepperRobot
from cloudroboconn import CloudROSConnector
import datetime
import json
import time

ws=CloudROSConnector()
pepper=PepperRobot()
try:
    ws.connect_client()
    pepper.connect()
    pepper.start_sensor_service("memoryProxy")
    pepper.start_sensor_service("dcm_service")

    while(True):
        laser_data=pepper.get_laser_data()
        s_data={
            'timestamp':datetime.datetime.now(),
            'data':laser_data
        }
        
        ws.send_data(s_data)
except Exception as e:
    print(e)

