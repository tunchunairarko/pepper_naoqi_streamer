import time
import edgeiq
import argparse
import socketio
import cv2
import base64
"""
Use object detection to detect objects in the frame in realtime. The
types of objects detected can be changed by selecting different models.

To change the computer vision model, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_model.html

To change the engine and accelerator, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_engine_and_accelerator.html
"""

sio = socketio.Client()


@sio.event
def connect():
    print('[INFO] Successfully connected to server.')


@sio.event
def connect_error():
    print('[INFO] Failed to connect to server.')


@sio.event
def disconnect():
    print('[INFO] Disconnected from server.')


class CVClient(object):
    def __init__(self, server_addr, stream_fps):
        self.server_addr = server_addr
        self.server_port = 5001
        self._stream_fps = stream_fps
        self._last_update_t = time.time()
        self._wait_t = (1/self._stream_fps)

    def setup(self):
        print('[INFO] Connecting to server http://{}:{}...'.format(
            self.server_addr, self.server_port))
        sio.connect(
                'http://{}:{}'.format(self.server_addr, self.server_port),
                transports=['websocket'],
                namespaces=['/cv'])
        time.sleep(1)
        return self

    def _convert_image_to_jpeg(self, image):
        # Encode frame as jpeg
        frame = cv2.imencode('.jpg', image)[1].tobytes()
        # Encode frame in base64 representation and remove
        # utf-8 encoding
        frame = base64.b64encode(frame).decode('utf-8')
        return "data:image/jpeg;base64,{}".format(frame)

    def send_data(self, frame):
        cur_t = time.time()
        if cur_t - self._last_update_t > self._wait_t:
            self._last_update_t = cur_t
            frame = edgeiq.resize(
                    frame, width=640, height=480, keep_scale=True)
            sio.emit(
                    'cv2server',
                    {
                        'image': self._convert_image_to_jpeg(frame)
                    })

    def check_exit(self):
        pass

    def close(self):
        sio.disconnect()


def main(server_addr, stream_fps):

    try:
        streamer = CVClient(server_addr, stream_fps).setup()

        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            # Generate text to display on streamer
            streamer.send_data(frame)
            if(cv2.waitKey(1) & 0xFF == ord('q')):
                break
            

    finally:
        if streamer is not None:
            streamer.close()
        print("Program Ending")


if __name__ == "__main__":
    main("robotstreamserver.isensetune.com", 30)
