#!/usr/bin/env python
import websocket
import json

class CloudROSConnector:
    def __init__(self,host="ws://robotstreamserver.isensetune.com",port="80"):
        self.host=host
        self.port=port
        websocket.enableTrace(True)
        self.__wsclient=websocket.WebSocket(enable_multithread=True)

        
    def connect_client(self):
        self.__wsclient.connect(self.host)
    def disconnect_client(self):
        self.__wsclient.close()
    def send_data(self,data="Hello world"):
        s_data={
            "robotdata":data
        }
        s_data=json.dumps(s_data)
        self.__wsclient.send(s_data)
        print(self.__wsclient.recv())

def main():
    ws=CloudROSConnector()
    ws.connect_client()
    data={
        "key":"900",
        "value":"er43"
    }
    
    ws.send_data(data)
    ws.disconnect_client()

if __name__=='__main__':
    main()