riche
=====

Reverse SSH for poors. -- uses Python Twisted

usage
=====

1. On a public server:
```bash
john@myserver$ riche-server 8577 8566
```

2. On a computer that you would like to access, but which is behind a NAT:
```bash
# openssh-server is listening on port 22
luke@mycomputer$ riche-client myserver.com 8577 22 "My Computer"
```

3. On an other computer, if you want to access the previous one:
```bash
me@home$ ssh luke@myserver.com -p 8566
```
(but first, you need to go on the web interface at http://myserver.com:8580 and to click on "My Computer")

Functionalities
===============

- should work with any TCP server (based on a simple single connection).
- riche-client handle network deconnections and will try to reconnect.
- access (on the port 8566 here) is restricted to an IP adress. This is easily done via a protected web interface.

Issues
======

- the access is restricted to one client at a time.
- ssh will warn you that the certificate is wrong for myserver.com.
- the riche-server should have restrictions on riche-clients.