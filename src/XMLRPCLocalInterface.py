#!/usr/bin/python

from xmlrpclib import ServerProxy, Fault
import os
import os.path
import logging

from TCPFunctions import *

XMLRPCPORT = 34001

class NodeLocalFault(Exception):
        """
        An exception in local handling code
        """
        def __init__(self, message="Interrupt when handling the query"):
            Exception.__init__(self, message)

class HostNotFoundFault(NodeLocalFault):
        pass


class NodeLocalFunctions:
    def __init__(self, nodemanager, downloaddir):
        self.nodemanager = nodemanager
        self.downloaddir = downloaddir
        self.TCPtransfers = []
        logging.info("[NodeLocalFunctions] initializing...")
        
    def _proxyiterate(self):
        """
        Starts the XML-RPC internal proxy
        """
        for node in self.nodemanager:
            s = self._getproxy(node)
            yield s
    def _getproxy(self,nodename):
        try:
            return ServerProxy("http://"+self.nodemanager[nodename]+":"+str(XMLRPCPORT))
        except KeyError:
            raise HostNotFoundFault

    def closeremote(self):
        s = ServerProxy("http://127.0.0.1:"+str(XMLRPCPORT))
        s.close()
    
    def getnodesinfo(self):
        infos = []
        for proxy in self._proxyiterate():
            infos.append((proxy.get_nodename(),proxy.get_nodeinfo()))
        return infos

    def node_shares(self,nodename):
        s = self._getproxy(nodename)
        return s.sharelist()
 
    def node_share_list(self,nodename,sharename,dirname):
        s = self._getproxy(nodename)
        return s.listshare(sharename,dirname)
    
    def search(self,kw):
        for node in self.nodemanager:
            yield self.node_search(node,kw)

    def node_search(self,nodename,kw):
        proxy = self._getproxy(nodename)
        result = proxy.search(kw)
        return (proxy.get_nodename(),result)
    
    
    def fetch(self,nodename,sharename,dirname,filename):
        proxy = self._getproxy(nodename)
        proxy.filetransfer(sharename, dirname, filename)
        
        t = TCP_connect_and_receive(filename,self.nodemanager[nodename],self.downloaddir)
        self.TCPtransfers.append(t)
        t.start()

