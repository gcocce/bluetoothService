'''
    This bluetooth Sever only accept one connection at a time.
    It listens for a connection, once connected checks connection status
    every DELAY_TIME seconds.
    If connection is lost it goes back to listen for a connecition and so on.

    It provides two non bloquing metods for sending and receiving text data:

        getData()

        sendData(data)
'''
#import os
import time
#import ctypes
import socket
import threading
import logging
import subprocess as sp
from bluetooth import *
from bluesender import *
from bluereceiver import *

SERVICE_NAME = "MyBluetoothService"
UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

DELAY_TIME = 1

class BlueServer(threading.Thread):
    @property
    def BUILDING(self):
        return 0
    @property
    def LISTENING(self):
        return 1
    @property
    def CONNECTED(self):
        return 2
    @property
    def DESCONNECTED(self):
        return 3
    @property
    def STOPPING(self):
        return 4
    @property
    def ERROR(self):
        return 5

    def __init__ (self):
        threading.Thread.__init__(self)
        logging.info("Init blueServer...")
        self.server_sock=BluetoothSocket( RFCOMM )
        self.server_sock.bind(("",PORT_ANY))
        self.server_sock.listen(1)
        self.port = self.server_sock.getsockname()[1]
        self.uuid = UUID
        self.client_sock = None
        self.receiver = None
        self.sender = None
        self.working=True
        self.status=self.BUILDING

        try:
            advertise_service(self.server_sock, SERVICE_NAME,
                               service_id = self.uuid,
                               service_classes = [ self.uuid, SERIAL_PORT_CLASS ],
                               profiles = [ SERIAL_PORT_PROFILE ],
                               )
        except BluetoothError as e:
            logging.error("Failed to start bluetooth: {}".format(e))
            import _thread
            _thread.interrupt_main()


    def run(self):
        while self.working:
            try:
                self.status=self.LISTENING
                logging.warning("Waiting for connection on RFCOMM channel {:d}".format(self.port))
                self.client_sock, self.client_info = self.server_sock.accept()
                logging.warning("Accepted connection from: {}".format(self.client_info))
                #Create and start threads for sender and receiver
                self.receiver = blueReceiver(self.client_sock)
                self.sender = blueSender(self.client_sock)
                self.receiver.start()
                self.sender.start()

                if (self.status==self.LISTENING):
                    self.status=self.CONNECTED
                    connected=True
                    while (connected):
                        stdoutdata = sp.check_output("hcitool con", shell=True)
                        # Two ways to find out if the connection is still alive
                        if self.client_info[0] in stdoutdata.split() and self.receiver.isRunning():
                            logging.info("Bluetooth device is connected...")
                        else:
                            logging.warning("Bluetooth device is no longer connected...")
                            connected=False
                            if (self.status != self.STOPPING):
                                self.status=self.DESCONNECTED
                                logging.info("blueServer cleaning structures...")
                                self.receiver.stop()
                                self.sender.stop()
                                self.client_sock.shutdown(socket.SHUT_RDWR)
                                self.client_sock.close()
                                self.sender.join()
                                self.receiver.join()
                                self.sender=None
                                self.receiver=None
                                self.client_sock = None
                        time.sleep(DELAY_TIME)
                    # ends while (connected)
            except IOError as e:
                logging.error ("IOError blueServer {}".format(e))
                self.status=self.DESCONNECTED
                raise
            except BluetoothError as e:
                logging.error ("BluetoothError blueServer {}".format(e))
                self.status=self.DESCONNECTED

        # ends while (self.working)
        logging.info ("blueServer ends")

    '''
        Non bloquing method
        If there is data it returns data otherwise nothing
    '''
    def getData(self):
        if self.receiver.isRunning():
            return self.receiver.getData()
        else:
            return ""

    '''
        Non bloquing method
    '''
    def sendData(self, data):
        if self.receiver.isRunning():
            self.sender.sendData(data)

    def getStatus(self):
        return self.status

    def isConnected(self):
        return (self.status == self.CONNECTED)

    def stop(self):
        logging.info ("stop blueServer...")
        if(self.status==self.CONNECTED):
            logging.info ("stop blueServer while connected...")
            self.working=False
            self.status= self.STOPPING
            self.receiver.stop()
            self.sender.stop()
            self.client_sock.shutdown(socket.SHUT_RDWR)
            self.client_sock.close()
            self.server_sock.close()
            self.sender.join()
            self.receiver.join()
        elif (self.status==self.LISTENING):
            logging.info ("stop blueServer while listenning...")
            self.working=False
            self.status= self.STOPPING
            logging.info ("try to stop bluetooth server socket...")
            self.server_sock.shutdown(socket.SHUT_RDWR)
            self.server_sock.close()
