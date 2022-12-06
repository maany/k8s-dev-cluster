# Introduction
A basic debug server to inspect headers of incoming requests

# Usage
Go to master node
```
vagrant ssh master
sudo su -
apt-get update && apt-get install -y python-pip
pip3 install flask
cd /vagrant/debug_server
FLASK_APP=app.py
flask run --host=172.16.16.10 --port=80
```
Then head to http://localhost on browser
and also try
```
prada.devmaany.com
```
to see the different request headers