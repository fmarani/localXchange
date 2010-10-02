import socket
from threading import Thread
from random import random
from time import sleep
import logging

class BroadcastGrouping(Thread):
    UDP_PORT=34000

    def __init__(self, member_name):
        Thread.__init__(self)
        self.sock = socket.socket( socket.AF_INET, # Internet
                     socket.SOCK_DGRAM ) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('',self.UDP_PORT))
        self.sock.settimeout(3)
        self.myname = member_name
        self.mybroadcastip = "<broadcast>"
        self.state = "RUNNING"
        self.mapping = {}
        logging.info("[BroadcastMapping] BROADCAST MAPPING started...")
        
    def bsend(self, message):
        self.sock.sendto( message, (self.mybroadcastip, self.UDP_PORT) )

    def brecv(self, bufferlen):
        return self.sock.recvfrom(bufferlen)

    def joinGroup(self):
        sleep(random())
        logging.debug("[BroadcastMapping] joining Group...")
        self.bsend(self.myname)
    
    def run(self):
        while 1:
            if self.state == "CLOSING":
                break
            if (not self.mapping.has_key(self.myname)):
                self.joinGroup()
            try:
                data = self.brecv(1024)
            except socket.timeout:
                continue
            msg = data[0]
            sender = data[1][0]
            if not (self.mapping.has_key(msg) and self.mapping[msg] == sender):
                # new entry nel gruppo
                logging.info("[BroadcastMapping] new member ["+msg+"], re-joining...")
                self.mapping.update({msg: sender})
                self.joinGroup()
        logging.info("[BroadcastMapping] closed.")
        self.sock.close();
        self.state = "CLOSED"
        
    def close(self):
        if (self.state == "RUNNING"):
            logging.info("[BroadcastMapping] closing...")
            self.state = "CLOSING"

    def __del__(self):
        self.close()

    def __len__(self):
        return len(self.mapping)
    def __getitem__(self,key):
        return self.mapping[key]
    def __iter__(self):
        return self.mapping.iterkeys()


