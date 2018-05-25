'''
    blueSender has the responsibility of sending data throught bluetooth socket
    it checks for data every DELAY_TIME seconds and send data when available
'''
import threading
import logging
import time

DELAY_TIME = 1

class blueSender(threading.Thread):
    def __init__ (self,sock):
        threading.Thread.__init__(self)
        logging.info("blueSender init...")
        self.sock = sock
        self.data = ""
        self.data_lock = threading.Lock()
        self.running=True

    def run(self):
        logging.info("blueSender starts...")
        try:
            while self.running:
                self.data_lock.acquire()
                if (len(self.data)!=0):
                    self.sock.send(self.data)
                    logging.info ("blueSender send [%s]" % self.data)
                    self.data=""
                self.data_lock.release()
                time.sleep(DELAY_TIME)
        except IOError:
            raise

        logging.info("blueSender run finishing...")
        self.running=False

    def sendData(self, data):
        self.data_lock.acquire()
        self.data = self.data + data
        self.data_lock.release()

    def isRunning(self):
        return self.running

    def stop(self):
        logging.info ("blueSender stops...")
        self.running=False
