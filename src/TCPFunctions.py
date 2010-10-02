import socket
from threading import Thread
import logging

TCP_PORT = 34100
BUFFER_SIZE = 1024
	

class TCP_listen_and_send(Thread):
	def __init__(self,filename):
		Thread.__init__(self)
		self.filename = filename
		self.state = "STARTING"
		logging.info("[TCP_listen_and_send: "+self.filename+"] listening for incoming connection...")
		
	def tcp_listen_and_send(self):
		f = open(self.filename,'rb')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('',TCP_PORT))
		s.listen(1)
		conn, addr = s.accept()
		self.state = "RUNNING"
		logging.info("[TCP_listen_and_send: "+self.filename+"] incoming connection from "+addr[0]+"...")
		while 1:
			if (self.state == "CLOSING"):
				break
			data = f.read(BUFFER_SIZE)
			if not data:
				break
			conn.send(data)
		conn.close()
		f.close()
		self.state = "CLOSED"
		logging.info("[TCP_listen_and_send: "+self.filename+"] transfer finished...")
	
	def run(self):
		self.tcp_listen_and_send()
	
	def close(self):
		if (self.state == "RUNNING"):
			logging.info("[TCP_listen_and_send: "+self.filename+"] aborting...")
			self.state = "CLOSING"


class TCP_connect_and_receive(Thread):
	def __init__(self,filename,destip,downloaddir):
		Thread.__init__(self)
		self.filename = filename
		self.destip = destip
		self.downloaddir = downloaddir
		self.state = "STARTING"
		logging.info("[TCP_connect_and_receive: "+self.filename+"] connecting...")
		
	def tcp_connect_and_receive(self):
		# called by client
		f = open(self.downloaddir + "/" + self.filename,'wb')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.destip, TCP_PORT))
		self.state = "RUNNING"
		logging.info("[TCP_connect_and_receive: "+self.filename+"] connected.")
		while 1:
			if (self.state == "CLOSING"):
				break
			data = s.recv(BUFFER_SIZE)
			if not data:
				break
			f.write(data)
		s.close()
		f.close()
		self.state = "CLOSED"
		logging.info("[TCP_connect_and_receive: "+self.filename+"] transfer finished.")

	def run(self):
		self.tcp_connect_and_receive()
		
	def close(self):
		if (self.state == "RUNNING"):
			logging.info("[TCP_connect_and_receive: "+self.filename+"] closing...")
			self.state = "CLOSING"