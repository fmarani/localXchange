#!/usr/bin/python

import BroadcastGrouping

import XMLRPCLocalInterface
import XMLRPCRemoteInterface

import common

from cmd import Cmd
from threading import Thread
from time import sleep
import sys
import xmlrpclib
import logging
import StringIO
import ConfigParser
import os.path
import string


class Client(Cmd):
    """
    A simple text-based interface to the NodeLocalFunctions class.
    """
    prompt = '> '
    intro = "LocalXchange V."+common.VERSION
    
    def __init__(self):
        Cmd.__init__(self)
        
        systems = common.start_system()
        
        self.log = systems['log']
        self.nodemanager = systems['nodemanager']
        self.remotefunc = systems['remotefunc']
        self.clientfunc = systems['clientfunc']
    
    def do_log(self,arg):
        print self.log.getvalue()
    
    def help_log(self):
        print "print the log"
        
    def do_getnodesinfo(self,arg):
        for nodeinfo in self.clientfunc.getnodesinfo():
            print nodeinfo[0], "-->", nodeinfo[1]
    
    def help_getnodesinfo(self):
        print """
Get nodes information for each connected node
Usage: getnodesinfo
        """
    
    def do_node_shares(self,arg):
        try:
            args = self.parseargs(arg)
            node = args[0]
        except IndexError:
            print "wrong parameters."
            self.help_node_shares()
        else:
            try:
                print node, " shares:"
                for dir in self.clientfunc.node_shares(node):
                    print "-> ",dir
            except XMLRPCLocalInterface.HostNotFoundFault:
                print "The node doesn't exist"

    
    def help_node_shares(self):
        print """
List shares on a certain node
Usage: node_shares <nodename>
        """

    def complete_node_shares(self,text, line, begidx, endidx):
        args = self.parseargs(line)
        is_typing_arg = text != ""
        
        at_arg = len(args)
        if not is_typing_arg:
            at_arg+=1
                
        if (at_arg == 2):
            return [x for x in self.nodemanager if x.startswith(text)]
        
        return []
        
    def do_node_share_list(self,arg):
        try:
            args = self.parseargs(arg)
            node = args[0]
            share = args[1]
            if len(args) == 3:
                dir = args[2]
            else:
                dir = ""
        except IndexError:
            print "wrong parameters."
            self.help_node_share_list()
        else:
            try:
                print node, " share ",share, " dir ",dir," has:"
                for f in self.clientfunc.node_share_list(node,share,dir):
                    print "-> ",f[0].ljust(32),"  (",f[1],")"
            except XMLRPCLocalInterface.HostNotFoundFault:
                print "The node doesn't exist"
            except xmlrpclib.Fault, fault:
                if fault.faultCode == XMLRPCRemoteInterface.ACCESS_DENIED:
                    print "Access denied: "+fault.faultString
                else:
                    print "Remote error: "+fault.faultString
    
    def help_node_share_list(self):
        print """
List files in a node share
Usage: node_share_list <nodename> <share> [dir]
        """
    
    def complete_node_share_list(self,text, line, begidx, endidx):
        args = self.parseargs(line)
        is_typing_arg = text != ""
        
        at_arg = len(args)
        if not is_typing_arg:
            at_arg+=1
                
        if (at_arg == 2):
            return [x for x in self.nodemanager if x.startswith(text)]
        if (at_arg == 3):
            args = self.parseargs(line)
            node = args[1]
            try:
                shares = self.clientfunc.node_shares(node)
                return [x for x in shares if x.startswith(text)]
            except:
                return []
#===============================================================================
#        if (at_arg == 4):
#            args = self.parseargs(line)
#            node = args[1]
#            share = args[2]
#            if is_typing_arg:
#                dir = args[3]
#            else:
#                dir = ""
#            try:
#                parent = string.join(dir.split("/")[0:-1],"/") # PARENT DIR
#                ls = self.clientfunc.node_share_list(node,share,parent)
#                #print ls
#                return [x[0]+"/" for x in ls if (x[1]['type'] == "D" and x[0].startswith(dir))]
#            except:
#                return []
#===============================================================================
        return []
     
    def do_search(self,arg):
        try:
            arg = self.parseargs(arg)
            kw = {}
            for i in range(0,len(arg),2):
                kw[arg[i]] = arg[i+1]
        except IndexError:
            print "wrong parameters"
            self.help_search()
        else:
            print "Search results of: ",kw
            for noderesult in self.clientfunc.search(kw):
                print noderesult[0], " results:"
                for shareresult in noderesult[1]:
                    print "IN SHARE: ",shareresult[0]
                    for f in shareresult[1]:
                        print "-> ",f[0].ljust(32)," subdir:",f[1].ljust(30),"  (",f[2],")"
        
    def help_search(self):
        print """
Search files over network, case insensitive
Usage: search <attribute value>+
where attribute can be: name, startdate

Example:
search name The_red_fox
search startdate 1929934788
search name fox startdate 1928349049
        """
    
    def complete_search(self,text, line, begidx, endidx):
        args = self.parseargs(line)
        is_typing_arg = text != ""
        
        at_arg = len(args)
        if not is_typing_arg:
            at_arg+=1
                
        if (at_arg % 2 == 0):
            return [x for x in ["name","startdate"] if x.startswith(text)]
        
        return []
        
    def do_node_search(self,arg):
        try:
            arg = self.parseargs(arg)
            node = arg[0]
            del arg[0]
            kw = {}
            for i in range(0,len(arg),2):
                kw[arg[i]] = arg[i+1]
        except IndexError:
            print "wrong parameters"
            self.help_node_search()
        else:
            try:
                print "Node search results of: ",kw
                noderesult = self.clientfunc.node_search(node,kw)
                print noderesult[0], " results:"
                for shareresult in noderesult[1]:
                    print "IN SHARE: ",shareresult[0]
                    for f in shareresult[1]:
                        print "-> ",f[0].ljust(32)," subdir:",f[1].ljust(30),"  (",f[2],")"
            except XMLRPCLocalInterface.HostNotFoundFault:
                print "The node doesn't exist"

    def help_node_search(self):
        print """
Search files on a node, case insensitive
Usage: search <attribute value>+

See help search for more information
        """

    def complete_node_search(self,text, line, begidx, endidx):
        args = self.parseargs(line)
        is_typing_arg = text != ""
        
        at_arg = len(args)
        if not is_typing_arg:
            at_arg+=1
                
        if (at_arg == 2):
            return [x for x in self.nodemanager if x.startswith(text)]
        if (at_arg % 2 == 1):
            return [x for x in ["name","startdate"] if x.startswith(text)]
        
        return []

    def do_fetch(self,arg):
        try:
            node, share, dir, filename = self.parseargs(arg)
        except ValueError:
            print "wrong parameters"
            self.help_fetch()
        else:
            try:
                self.clientfunc.fetch(node, share, dir, filename)
            except XMLRPCLocalInterface.HostNotFoundFault:
                print "the node doesn't exist"
            except xmlrpclib.Fault, fault:
                if fault.faultCode == XMLRPCRemoteInterface.ACCESS_DENIED:
                    print "Access denied"
                else:
                    if fault.faultCode == XMLRPCRemoteInterface.FILE_NOT_FOUND:
                        print "File ",filename," not found"
                    else:
                        print "Remote error"
    
    def help_fetch(self):
        print """
Fetch a file in a share on a node
Usage: fetch <node> <share> <dir> <filename>
        """
    
    def complete_fetch(self,text, line, begidx, endidx):
        args = self.parseargs(line)
        is_typing_arg = text != ""
        
        at_arg = len(args)
        if not is_typing_arg:
            at_arg+=1
                
        if (at_arg == 2):
            return [x for x in self.nodemanager if x.startswith(text)]
        if (at_arg == 3):
            args = self.parseargs(line)
            node = args[1]
            try:
                shares = self.clientfunc.node_shares(node)
                return [x for x in shares if x.startswith(text)]
            except:
                return []
        return []    
            
    def parseargs(self,args_string):
        args = []
        buffer = ""
        in_brackets = False
        for i in args_string:
            if (i == "\""):
                in_brackets = not in_brackets
                continue
            if (i not in string.whitespace or in_brackets):
                buffer += i
                continue
            if (i in string.whitespace and len(buffer) > 0):
                args.append(buffer)
                buffer = ""
                continue
        if (len(buffer) > 0):
            args.append(buffer)
        return args
            
    def do_transferstatus(self,arg):
        for i in self.clientfunc.TCPtransfers:
            print i.filename, "-->", i.state
    
    def help_transferstatus(self):
        print """
See status of current session transfers
Usage: transferstatus
"""

    def do_exit(self, arg):
        "Exit the program."
        print "Exit..."
        self.nodemanager.close()
        self.clientfunc.closeremote()
        while (self.nodemanager.state != "CLOSED" and self.remotefunc.state != "CLOSED"):
            pass
        sys.exit()

    def help_exit(self):
        print "Exit the program"

    do_EOF = do_exit # End-Of-File is synonymous with 'exit'

def main():
    client = Client()
    try:
        client.cmdloop()
    except:
        sys.exit()

if __name__ == '__main__': main()

