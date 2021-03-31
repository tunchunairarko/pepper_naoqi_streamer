from pepper_laser import PepperRobot
from cloudroboconn import CloudROSConnector
import datetime

import json
import time

def getCurrentTimeStamp():
    dt = datetime.datetime.utcnow()
    timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    return timestamp

def main():
    ws=CloudROSConnector()
    pepper=PepperRobot()
    try:
        ws.connect_client()
        pepper.connect()
        pepper.start_motion_service()
        pepper.start_sensor_service("memoryProxy")
        pepper.start_sensor_service("dcm_service")

        # print("1")
        while(True):
            # print("3")
            laser_data=pepper.get_laser_data()
            # dt=datetime.datetime.now()
            # utc_timestamp=dt.timestamp()
            
            s_data={
                'timestamp':getCurrentTimeStamp(),
                'data':laser_data
            }
            
            ws.send_data(data=s_data)
            # print("2")
            time.sleep(0.001)
    except Exception as e:
        ws.disconnect_client()
        print("line 37")
        print(e)

if __name__=='__main__':
    main()

