import time
import logging
import pitemp
from blueServer import *

# Delay time to repeate this script's main cycle
DELAY_TIME = 1

logging.basicConfig(level=logging.INFO)

'''
    Create bluetooth server and start linstening for connection
'''
blueServer = BlueServer()
# Start bluetooth Server main thread
blueServer.start()

'''
    Your script main cycle starts here
    BlueServer runs on it own thread

'''
logging.info ("myScript starts...")
cycle=True
while cycle:
    try:
        if (blueServer.isConnected()):
            data = blueServer.getData()
            if data and len(data)!=0:
                logging.info ("myScript has data to process :)")
            	if data == 'temp':
                    # ask for raspberry pi procesor temperature
            		data = str(pitemp.read_temp())
            	elif data == 'end':
                    # finish myScript
            		cycle = False
            	elif data == 'on':
                    # do something with this command
                    # like turn a led on
            		data = 'on!'
            	elif data == 'off':
                    # do something with this command
                    # like turn a led off
            		data = 'off!'
            	else:
            		data = 'WTF!'
                blueServer.sendData(data)
            	logging.info("myScript send: [%s]" % data)

        time.sleep(DELAY_TIME)

    # It can only be interrupted from client!!!
    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt...")
        cycle=False

# Stop server and wait for main thread to finish
blueServer.stop()
blueServer.join()
logging.info( "All done")
