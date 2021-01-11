from imutils.video import VideoStream
import imagezmq
import argparse
import socket
import time

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
    help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

print('Connecting to IMAGEZMQ server')
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
    args["server_ip"]))

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()
vs = VideoStream(usePiCamera=True).start()
#vs = VideoStream(src=0).start()
time.sleep(2.0)
 
while True:
    frame = vs.read()
    sender.send_image(rpiName, frame)(cv)