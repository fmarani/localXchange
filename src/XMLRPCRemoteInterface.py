#!/usr/bin/python

from xmlrpclib import ServerProxy, Fault
import os
import os.path
from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Thread
import logging
import string

from TCPFunctions import *

SimpleXMLRPCServer.allow_reuse_address = 1
XMLRPCPORT = 34001

UNHANDLED = 100
ACCESS_DENIED = 200
FILE_NOT_FOUND = 404

class NodeRemoteFault(Fault):
        """
        An exception that represents an unhandled query.
        """
        def __init__(self, errorcode=UNHANDLED, message="Interrupt when handling the query"):
                Fault.__init__(self, errorcode, message)

class NodeRemoteFunctions(Thread):
        """
        XML-RPC Remote Control Functions
        """
        def __init__(self, nodename, shares):
                Thread.__init__(self)
                # self.shares format: [(sharename, sharedir), ...]
                self.shares = shares
                self.nodename = nodename
                self.TCPtransfers = []
                self.state = "INITIALIZED"
        
        def get_nodename(self):
                return self.nodename
            
        def get_nodeinfo(self):
                return "NOT YET IMPLEMENTED"

        def search(self,kw):
                result = []
                for share in self.shares:
                    dirname = share[1]
                    res = self._dirsearchrecursive(dirname,kw)
                    result.append((share[0],res))          
                return result
        
        def _dirsearchrecursive(self,basedir,kw,subdirstack=[]):
                filelist = []
                subdirs = string.join(subdirstack,"/")
                dirname = basedir + "/" + subdirs
                for filename in os.listdir(dirname):
                        filecomplete = os.path.join(dirname,filename)
                        if (os.path.isfile(filecomplete)):
                            if kw.has_key("name") and filename.lower().find(kw['name'].lower()) != -1:
                                filelist.append((filename,subdirs,self._getproperties(filecomplete)))
                            else:
                                if kw.has_key("startdate"):
                                    try:
                                        if os.path.getmtime(filecomplete) > int(kw['startdate']):
                                            filelist.append((filename,subdirs,self._getproperties(filecomplete)))    
                                    except ValueError:
                                        pass
                        else:
                            if (os.path.isdir(filecomplete)):
                                clonesub = list(subdirstack)
                                clonesub.append(filename)
                                for r in self._dirsearchrecursive(basedir,kw,clonesub):
                                    filelist.append(r)
                return filelist
        
        def sharelist(self):
                return [x[0] for x in self.shares]

        def _getdirectory(self,sharename,dirname=""):
                for share in self.shares:
                    if share[0] == sharename:
                        base = share[1]
                        dir = os.path.abspath(base+"/"+dirname)
                        if (dir[0:len(base)] == base):
                            return dir
                raise NodeRemoteFault(ACCESS_DENIED,"share/dir not allowed")
        
        def _getproperties(self,file):
                properties = {}
                if (os.path.isdir(file)):
                    properties['type'] = "D"
                else:
                    if (os.path.isfile(file)):
                        properties['type'] = "F"
                properties['mtime'] = os.path.getmtime(file)
                # OTHER PROPERTIES WILL COME!!
                return properties
        
        def listshare(self,sharename,dirname):
                filelist = []
                
                dirname = self._getdirectory(sharename,dirname)
                
                if not (os.path.isdir(dirname)):
                        raise NodeRemoteFault(FILE_NOT_FOUND,dirname + " dir not found")
                
                for f in os.listdir(dirname):
                        filelist.append((f,self._getproperties(os.path.join(dirname,f))))
                
                return filelist 

        def filetransfer(self, sharename, dirname, filename):
                dirname = os.path.abspath(self._getdirectory(sharename, dirname))
                filename = os.path.basename(filename)
                filecomplete = os.path.join(dirname, filename)

                if not (os.path.isfile(filecomplete) and os.access(filecomplete,os.R_OK)):
                        raise NodeRemoteFault(FILE_NOT_FOUND,filecomplete + " not found or read error")
                
                self._tcptransfer(filecomplete)
                return True
                
        def _tcptransfer(self,file):
                t = TCP_listen_and_send(file)
                self.TCPtransfers.append(t)
                t.start()

        def close(self):
                if (self.state == "RUNNING"):
                    logging.info("[NodeRemoteFunctions] closing...")
                    self.state = "CLOSING"
                    return True
                return False
            
        def run(self):
                """
                Used internally to start the XML-RPC server.
                """
                logging.info("[NodeRemoteFunctions] initializing...")
                s = SimpleXMLRPCServer(("", XMLRPCPORT), logRequests=False)
                s.register_instance(self)
                self.state = "RUNNING"
                while 1:
                    if self.state == "CLOSING":
                        break
                    s.handle_request()
                self.state = "CLOSED"
                logging.info("[NodeRemoteFunctions] closed.")
                

