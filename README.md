# MiLight-Web

MiLight-Web is a complete web interface for your MiLight setup. It uses the MiLight Control Interface, which is a powerful Python API to control MiLight LED bulbs and strips (White and RGBW).

Development, updates, feature requests, etc. see [https://github.com/hanckmann/MiLight-Web](https://github.com/hanckmann/MiLight-Web).

It supports al basic interface operations, and a few more.

MiLight products are also known under the name LimitlessLED, and EasyBulb Lamps.

## How to install

Checkout the source from github:

    git clone https://github.com/hanckmann/MiLight-Web.git

First create a Python 3 virtual environment (or install the required packages directly), activate the virtual environment, and install the required packages:

    cd MiLight-Web
    python3 -m venv flask
    source flask/bin/activate
    pip install -r requirements.txt

Now MiLight-Web is ready for action.

## Start/test MiLight-Web

Make sure there is at the least one MiLight brige on your network, and test the application. First make sure that you are in the virtual environment:

    source flask/bin/activate
 
 Start MiLight-Web:

    ./run.py

Running MiLight-Web in this way works, but is not recommended (security and performance reasons).

## Setup nginx to work with MiLight-Web

It is recommended to use wsgi and nginx to run MiLight-Web. When enables via systemd, this also ensures that it start automatically after a reboot.

### Install nginx

Depending on your distro, install nginx using your application repository (apt, pacman, etc.).

### Setup your system

First setup a systemd service to start wsgi with MiLight-Web. Make sure to replace the parts enclosed in <>, with the correct values (paths or names).

Create a text file named *milightweb.service* with the following content:

```text
[Unit]
Description=uWSGI instance to serve MiLight-Web
After=network.target

[Service]
User=patrick
Group=http
WorkingDirectory=<MILIGHT_WEB_PATH>
Environment="PATH=<MILIGHT_WEB_PATH>/flask/bin"
ExecStart=<MILIGHT_WEB_PATH>/flask/bin/uwsgi --ini uwsgi.ini

[Install]
WantedBy=multi-user.target
```

Replace <MILIGHT_WEB_PATH> with the path containing the *run.py* (where you/git cloned the repository).

Create a text file named *uwsgi.ini* with the following content:

```text
[uwsgi]
module = wsgi:app

master = true
processes = 3

socket = /home/patrick/mw/milightweb.sock
chmod-socket = 666
vacuum = true

die-on-term = true
```

Replace <MILIGHT_WEB_PATH> with the path containing the *run.py* (where you/git cloned the repository).

Create a text file named *nginx.conf* with the following content:

```text
server {
  listen 80;
  # server_name server_domain_or_IP;

  root /var/www/html;

  location / {
    include uwsgi_params;
    uwsgi_pass unix://<MILIGHT_WEB_PATH>/milightweb.sock;
  }
}
```

Replace <MILIGHT_WEB_PATH> with the path containing the *run.py* (where you/git cloned the repository).

We now have three files created:

- milightweb.service
- uwsgi.ini
- nginx.conf

Now copy the files to the correct locations. *Note* that this must be done as root user (sudo). *Note* that these location might be different depending on your Linux distribution (tested on ArchLinux):

    cp milightweb.service /etc/systemd/system/
    cp nginx.conf /etc/nginx/sites-enabled/milightweb.conf

*Note* the name change for nginx.conf.

### Start the system

Now it is time to test and start your system. First check (as root/sudo) if nginx likes your configuration (or if it has errors):

    nginx -t

Then start the milightweb and nginx service (as root/sudo):

    systemctl start milightweb.service
    systemctl start nginx

After this your MiLight-Web instance should be reachable via the computers IP address [127.0.0.1](https://127.0.0.1/milight)

## Notes

The installation notes are (currently) written as I remember them. These need refinement and this will be done eventually. 

The installation notes are based on a Raspberry Pi with ArchLinux. Some steps might take a long time to complete (for example installing the requirements.txt, where the uwsgi needs to compile some files).

~~ Patrick