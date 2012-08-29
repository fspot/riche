#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ============== WEB ===============

# run in under twisted through wsgi
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from flask import Flask, request, url_for, redirect, render_template, flash, session

from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
from time import sleep
import os, sys
import datetime
from functools import wraps
from ConfigParser import ConfigParser

# ===== globals =====

noms = {}
destinations = []


# -------------------- 
# -----  Flask  ------
# --------------------

app = Flask(__name__)

def requires_root(vue):
    @wraps(vue)
    def decorated(*args, **kwargs):
        if session.get('pw') != app.password:
            return redirect(url_for('login'))
        return vue(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['pw'] = request.form['pw']
        return redirect(url_for('liste'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('pw', None)
    return redirect(url_for('liste'))

@app.route("/nom/<nom>")
@requires_root
def set_ip(nom):
    for n in noms:
        if noms[n] == request.remote_addr:
            noms[n] = ''
    noms[nom] = request.remote_addr
    for d in destinations:
        if d.nom == nom:
            d.ip_ok = request.remote_addr
        else:
            if d.ip_ok == request.remote_addr:
                d.ip_ok = ''
    flash(u'Le serveur "{0}" vous est accessible !'.format(nom), 'succes')
    print '  @ {0} has access to server {1}.'.format(request.remote_addr, nom)
    return redirect(url_for('liste'))

@app.route("/clear/<nom>")
@requires_root
def clear_ip(nom):
    noms[nom] = ''
    for d in destinations:
        if d.nom == nom:
            d.ip_ok = ''
    flash(u'Le serveur "{0}" ne vous est plus accessible !'.format(nom), 'error')
    return redirect(url_for('liste'))

@app.route("/")
@requires_root
def liste():
    return render_template('liste.html', machines=destinations, ip=request.remote_addr)

# ---------------------------- 
# -----  SERVER source  ------
# ----------------------------

class Source(Protocol):
    def __init__(self):
        self.recu = ''
        self.dest = None
    
    def connectionMade(self):
        print "<Source connection made from {0}>".format(self.transport.client[0])
        dest = None
        for d in destinations:
            if d.ip_ok == self.transport.client[0]:
                print "<ip found>"
                dest = d
                break
        if dest is None:
            self.transport.loseConnection()
            return
        else:
            self.dest = dest
            self.dest.source = self
            if self.dest.recu:
                print "<sending old data>"
                self.w(self.dest.recu)
                self.dest.recu = ''
    
    def connectionLost(self, reason):
        print "<Source connection lost>"
        if self.dest is not None:
            self.dest.transport.loseConnection()

    def dataReceived(self, data):
        if self.dest is not None:
            self.dest.w(data)
        else:
            print "<Dest is not connected yet>"
            self.transport.loseConnection()

    def w(self, data):
        self.transport.write(data)


class SourceFactory(Factory):
    def buildProtocol(self, addr):
        return Source()


# ---------------------------- 
# -----   SERVER dest   ------
# ----------------------------

class Dest(Protocol):
    def __init__(self):
        self.recu = ''
        self.ip_ok = ''
        self.nom = 'nom'
        self.source = None
        self.state = 'NAME' # in ['NAME', 'NORMAL']
    
    def connectionMade(self):
        print "<Dest connection made>"
        destinations.append(self)
    
    def connectionLost(self, reason):
        print "<Dest connection lost>"
        destinations.remove(self)

    def dataReceived(self, data):
        if self.state == 'NAME':
            self.nom = data
            print "<Dest name is {0}>".format(self.nom)
            if self.nom in noms:
                self.ip_ok = noms[self.nom]
                print "<Dest is accessible via {0}>".format(self.ip_ok)
            self.state = 'NORMAL'
        elif self.state == 'NORMAL':
            if self.source is None:
                self.recu += data
                if len(self.recu) > 10000:  # 10 ko
                    self.transport.loseConnection()
            else:
                self.source.w(data)

    def w(self, data):
    	self.transport.write(data)


class DestFactory(Factory):
    def buildProtocol(self, addr):
        return Dest()


# =========== main ============

if __name__ == '__main__':

    config = ConfigParser()
    config.read('richeserver.ini')

    app.debug = config.getboolean('conf', 'flask_debug')
    app.secret_key = config.get('conf', 'flask_secret_key')
    app.password = config.get('conf', 'flask_password')
    
    reactor.listenTCP(config.getint('conf', 'port_dest'), DestFactory())
    reactor.listenTCP(config.getint('conf', 'port_access'), SourceFactory())

    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
    reactor.listenTCP(config.getint('conf', 'port_flask'), site)

    print "<server launched>"

    reactor.run()