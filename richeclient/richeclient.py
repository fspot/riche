#!/usr/bin/env python
# -*- coding:utf-8 -*-

from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
from time import sleep
import os, sys
import datetime
from multiprocessing import Process
from ConfigParser import ConfigParser

# === config / globaux ===

conf = {}

class Global(object):
	def __init__(self):
		self.server = None
		self.client = None

g = Global()

# CLIENT OpenSSH

class LocalClient(Protocol):
    def __init__(self):
        self.recu = ""

    def connectionMade(self):
    	print "<... done.>"
    	g.client = self
    
    def connectionLost(self, reason):
        print "<client connection lost : {0}>".format(reason)
        g.client = None
        if g.server is not None:
            g.server.transport.loseConnection()
        d = conf['point2'].connect(ServerClientFactory())
        def myc(e):
            print "<Connection error : retrying in 10s>"
            reactor.callLater(10, foo)
        d.addErrback(myc)

    def dataReceived(self, data):
        if g.server:
        	g.server.w(data)

    def w(self, data):
    	self.transport.write(data)


class LocalClientFactory(Factory):
    def buildProtocol(self, addr):
        return LocalClient()


# CLIENT Server

class ServerClient(Protocol):
    def __init__(self):
        self.recu = ''
    
    def connectionMade(self):
        print "<... done.>"
        g.server = self
        self.w(conf['NOM'])
        print "<connecting to local port...>"
        d = conf['point'].connect(LocalClientFactory())
    
    def connectionLost(self, reason):
        print "<server connection lost : {0}>".format(reason)
        g.server = None
        if g.client is not None:
            g.client.transport.loseConnection()

    def dataReceived(self, data):
        g.client.w(data)

    def w(self, data):
    	self.transport.write(data)


class ServerClientFactory(Factory):
    def buildProtocol(self, addr):
        return ServerClient()

# =========== main function of the process ============

def foo():
    print "<connecting to S...>"
    d = conf['point2'].connect(ServerClientFactory())
    def myc(e):
        print "<Connection error : retrying in 10s>"
        reactor.callLater(10, foo)
    d.addErrback(myc)
    if not reactor.running:
        reactor.run()

# ========= class that wraps process ============

class Riche(object):
    """ objet que l'on manipule pour stopper/redemarrer la fonction principale. """
    def __init__(self, nom, port_local, ip_s, port_s):
        conf['NOM'] = nom
        conf['PORT_LOCAL'] = port_local
        conf['IP_S'] = ip_s
        conf['PORT_S'] = port_s
        conf['point'] = TCP4ClientEndpoint(reactor, "127.0.0.1", conf['PORT_LOCAL'])
        conf['point2'] = TCP4ClientEndpoint(reactor, conf['IP_S'], conf['PORT_S'])
        self.process = None
    
    def _launch(self):
        self.process = Process(target=foo)
        self.process.start()
    
    def stopped(self):
        return self.process == None
    
    def stop(self):
        if not self.stopped():
            if self.process.is_alive():
            
                # self.process.terminate()  # does not work on linux =(.. Replacement:
                os.system('kill -9 {0}'.format(self.process.pid))  # ugh !
                
                while self.process.is_alive():
                    pass
            self.process = None
            
    def start(self):  # (re)démarre 
        self.restart()
    
    def restart(self):  # (re)démarre 
        if not self.stopped():
            self.stop()
        self._launch()


# =========== main ============

def make_riche():
    config = ConfigParser()
    config.read('richeclient.ini')

    ip_s = config.get('conf', 'ip_s')
    port_s = config.getint('conf', 'port_s')
    port_local = config.getint('conf', 'port_local')
    nom = config.get('conf', 'nom')

    riche = Riche(nom, port_local, ip_s, port_s)
    return riche


if __name__ == '__main__':
    riche = make_riche()
    print '<Hi!>'
    riche.start()
    while raw_input("<Enter 'quit' if you want to>") != 'quit':
        pass
    riche.stop()
    print '<Bye!>'

