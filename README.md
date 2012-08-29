riche
=====

Reverse SSH for poors. -- uses Python Twisted

usage
=====

1. On a public server:
```bash
john@myserver ~/riche/richeserver $ python richeserver.py
```

2. On a computer that you would like to access, but which is behind a NAT:
```bash
# we assume that openssh-server is listening on port 22
luke@mycomputer ~/riche/richeclient $ python richeclient.py
```

3. On an other computer, if you want to access the previous one:
```bash
me@home ~ $ ssh luke@myserver.com -p 8566
```
(but first, you need to go on the web interface at http://myserver.com:8580 and to click on "My Computer")

configuration
=============

1. richeserver config :
```bash
john@myserver ~/riche/richeserver $ cat richeserver.ini
[conf]
flask_secret_key: s486t$`§§!4v1dg846AHR(($$
flask_debug: false
flask_password: toto
port_dest: 8577
port_access: 8566
port_flask: 8580
```
You need python2, twisted and flask.

2. richeclient config :
```bash
luke@mycomputer ~/riche/richeclient $ cat richeclient.ini
[conf]
nom: SSH on luke's computer
port_local: 22
ip_s: myserver.com
port_s: 8577
```
You need python2 and twisted.

Functionalities
===============

- should work with any TCP server (based on a simple single connection).
- richeclient handle network deconnections and will try to reconnect.
- access (on the port 8566 here) is restricted to an IP adress. This is easily done via a protected web interface.

Issues
======

- the access is restricted to one client at a time.
- ssh will warn you that the certificate is wrong for myserver.com.
- the richeserver should have restrictions on richeclients.