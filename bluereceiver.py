'''
    blueReceiver has the responsability of receiving data from bluetooth socket
    Main thread blocks on socket.recv waiting for any data available.
    When socket connection breaks a BluetoothError exception is raised
    and main thread finish.
'''
import threading
import logging
from bluetooth import BluetoothError

class blueReceiver(threading.Thread):
    def __init__ (self,sock):
        threading.Thread.__init__(self)
        logging.info ("blueReceiver init...")
        self.sock = sock
        self.data = ""
        self.data_lock = threading.Lock()
        self.running=True

    def run(self):
        logging.info("blueReceiver starts...")
        try:
            while self.running:
                data = self.sock.recv(1024)
                if len(data) == 0: break
                logging.info ("blueReceiver received [%s]" % data)
                self.data_lock.acquire()
                self.data = self.data + data
                self.data_lock.release()
        except BluetoothError:
            logging.warning ("BluetoothError bluereceiver")
            self.running=False
        except IOError:
            raise

        logging.info ("blueReceiver run finishing...")
        self.running=False

    def getData(self):
        self.data_lock.acquire()
        data = self.data
        self.data=""
        self.data_lock.release()
        return data

    def isRunning(self):
        return self.running

    def stop(self):
        logging.info ("blueReceiver stop...")
        self.running=False
