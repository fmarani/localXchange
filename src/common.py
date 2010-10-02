#!/usr/bin/python

import ConfigParser
import StringIO
import os.path
import logging
import string

import BroadcastGrouping
import XMLRPCLocalInterface
import XMLRPCRemoteInterface

VERSION = "0.02"

def start_system():
        systems = dict()
        config = ConfigParser.ConfigParser()
        config.read("config.txt")
        
        try:
            NODE_NAME = config.get("node", "name")
            SHARES = config.items("shares")
            DOWNLOAD_DIR = config.get("node","downloaddir")
        except ConfigParser.NoSectionError:
            print "No config found."
            sys.exit(1)
        except ConfigParser.NoOptionError, e:
            print "Configuration error: ",str(e)
            sys.exit(1)
        
        systems['log'] = StringIO.StringIO()
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            stream=systems['log'])
        logging.info("LocalXchange V." + VERSION + " starting...")
        logging.info("node name = " + NODE_NAME)
        logging.info("download dir = " + DOWNLOAD_DIR)
        logging.info("share list:")
        for s in range(len(SHARES)):
            logging.info(SHARES[s][0] + " -> " + SHARES[s][1])
            if not (os.path.isdir(SHARES[s][1])):
                logging.error(SHARES[s][1] + " is not a directory!")
                del SHARES[s]
        
        for letter in NODE_NAME:
            if (letter not in string.letters and letter not in string.digits):
                print "node name not valid (only letters and digits)"
                sys.exit(1)
        
        if not (os.path.isdir(DOWNLOAD_DIR)):
            print "DOWNLOAD dir doesn't exist"
            sys.exit(1)
        
        systems['nodemanager'] = BroadcastGrouping.BroadcastGrouping(NODE_NAME)
        systems['nodemanager'].start()

        systems['remotefunc'] = XMLRPCRemoteInterface.NodeRemoteFunctions(NODE_NAME,SHARES)
        systems['remotefunc'].start()

        systems['clientfunc'] = XMLRPCLocalInterface.NodeLocalFunctions(self.nodemanager,DOWNLOAD_DIR)
        return systems
