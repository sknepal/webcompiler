# Webcompiler
Compile code online. Uses python on the backend and xterm.js terminal emulator on the frontend. Useful for online (code) judges, programming sites. 

## Packages Required
* tornado: python web server. 
* terminado: websocket backend for xterm.js.
* gcc: c compiler.
* python-dev: dev tools, header files.
* gevent: enables concurrency.
* flask: python web development framework.
* flask-restful: flask library for REST api.
* flask-cors: handles CORS in flask.
* gunicorn: python WSGI server.
* firejail: linux sandbox.
* nginx: web server.

## Installation

* sudo apt-get install python-pip
* sudo pip install tornado terminado
* sudo pip install gunicorn flask
* sudo apt-get install gcc
* sudo apt-get install python-dev
* sudo pip install gevent
* sudo pip install flask-restful
* sudo pip install flask-cors
* sudo apt-get install nginx

Download and install firejail from: [firejail.wordpress.com](http://firejail.wordpress.com) (there could be a different version available at the time. So, make sure to check for one on their official website: firejail.wordpress.com. After finding the recent release, you should do something along the lines of: )

```
wget https://downloads.sourceforge.net/project/firejail/firejail/firejail_0.9.50_1_amd64.deb
sudo dpkg -i firejail_0.9.50_1_amd64.deb
```

## Setup Guide

### What's happening?

**Please read [this blog post](https://www.thelacunablog.com/make-online-code-compiler.html) first to understand the general flow of the system.**

### Setup User
1. First of all, create a new user with sudo access on the Server following the instructions here: https://www.digitalocean.com/community/tutorials/how-to-create-a-sudo-user-on-ubuntu-quickstart
2. SSH via the newly created user and follow the guidelines below. Do not use ROOT user.
```
ssh newuser@serveraddress
```

### Setup API

1. Copy compilerapi.py and wsgi.py to /home/username folder
  * For API setup, we're going to basically follow the guide: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-14-04 
2. Create an upstart file:
```
  sudo vi /etc/init/compilerapi.conf
```
3.	Insert the following text in the file (or simply copy it from the provided compilerapi.conf file.) 
**NOTE**: 'try' is the username of the current user (ie the user that we created above.), so replace it accordingly for you.
```
description "Gunicorn application server running compiler api"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid try
setgid www-data

env PATH=/tmp:/home/try/tmp:/home/try/bin:/usr/lib:/home/try/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
chdir /home/try
exec gunicorn --bind unix:compiler.sock --workers 10  --pid gunicorn --log-level=debug --log-file /home/try/gunlog -t 300 -m 007 --worker-class gevent wsgi:app
```

4. Save the file.
5. Create nginx configuration. 
```
cd /etc/nginx/sites-available
vi compilerapi
```
6. Insert the following in the file. **NOTE**: Replace IP_ADDRESS with the IP of the server where you are running it.
```
server {
    listen 81;
    server_name IP_ADDRESS;
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/try/compiler.sock;
    }
}
```
7. Save the file.
8. Create a symbolic link to it from sites-enabled: 
```
sudo ln -s /etc/nginx/sites-available/compilerapi /etc/nginx/sites-enabled
```
9. Done. Now, start compilerapi and restart NGINX.
```
sudo start compilerapi
sudo service nginx restart
```

### Setup HTML File
1. Edit the HTML File C.html.
  * Search for 'host' and replace it with your server's (IP) address:
  
  *ie. line 191 --> url: 'https://host:81/C/',*
  * The line 109 might cause problem. 
     
  *ie.  if ((term.title != "try@host: ~") && (term.title != "try@host: /home/try")) {*
    
  Here the code is basically trying to check if the terminal is loaded on the site or not. So it is checking the prompt and if the prompt is equal to *try@host* or *try@host: /home/try* then its saying the terminal is not loaded yet. Depending upon the username of the system, you will need to change 'try' to your username and 'host' to your IP. If you are still having problem: try removing this 'if case' and see what comes up as prompt on the terminal and then use that prompt for conditional check here later on.
	
### Setup Terminal Backend
1. First locate where tornado package is installed. In most cases it is installed in the `/usr/local/lib/python2.7` directory. You can find out by entering `locate tornado` on the terminal.
2. Edit the *websocket.py* file and make the following changes. 
  * On ***def check_origin***: comment everything and add new line: ***return True***
3. In order to make sure that Firejail is exited upon websocket close, add the following in the terminado/management.py:
```
from subprocess import call
import subprocess

def killfj(self,sig=signal.SIGTERM):
    pgid = os.getpgid(self.ptyproc.pid)
    subprocess.call(["firejail","--shutdown="+str(pgid)])
```

4. Modify the UniqueTermManager within the same file:
```
def client_disconnected(self, websocket):
    """Send terminal SIGHUP when client disconnects."""
    self.log.info("Websocket closed, sending SIGHUP to terminal.")
    if websocket.terminal:
        websocket.terminal.killfj(signal.SIGHUP)
```

5. In /home/yourusername/, put the C.html file and css folder.
6. Give proper access rights to the /tmp folder.
```
sudo su
cd /
chown YOUR_USER_NAME:YOUR_USER_NAME tmp
```

  * The tmp directory needs to be owned by user who is going to run it. ***NOTE:*** Change 'YOUR_USER_NAME' to whatever user you've created above.
7. Change the nginx configuration to pass requests on port 80 to 8079 and accept websocket requests.
  * Open the default config file:
```
cd /etc/nginx/sites-available
sudo vi default
```

  *  Add the following inside *server* to proxy-pass requests on port 80 to port 8079 where the tornado server is accepting requests. ***NOTE:*** Replace YOUR_SERVER_IP_ADDRESS with the appropriate address of your server.:
```
	location / {
	proxy_pass http://YOUR_SERVER_IP_ADDRESS:8079;
	proxy_set_header X-Real-IP $remote_addr;
	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	proxy_set_header Host $http_host;
	proxy_set_header X-NginX-Proxy true;

	#Enables WS Support
	proxy_http_version 1.1;
	proxy_set_header Upgrade $http_upgrade;
	proxy_set_header Connection "upgrade";
	proxy_redirect off;
	}
```
8. Replace all *'try'* in app.py with your username. 
9. Run the app. It should now be working
```
cd ~
python app.py
```

### Setup Compiler
1. Open up ~/.bashrc and export /tmp as a PATH variable
```
cd ~/.bashrc
export PATH=$PATH:/tmp
```

  * This is just to make sure that we don't need to hit '/' in order to run the applications since '/' is disallowed in restricted bash (ie rbash).
2. Depending upon the code you are compiling, you may need different compilers. For example, Mono compiler for C#, Kotlin compiler etc. Since we are only compiling C, we will need gcc.
```
sudo apt-get install gcc
```

  * Ways to setup some other compilers:
    * Mono Compiler for C#: ```sudo apt-get install mono-complete```
    * For C++: ```sudo apt-get install g++```
    * For Java:
    ```
       sudo add-apt-repository ppa:webupd8team/java
       sudo apt-get update
       sudo apt-get install oracle-java8-installer
	  ```
    * For Kotlin
	  ```sudo apt-get install unzip
       sudo apt-get install zip
       curl -s https://get.sdkman.io | bash
       sdk install kotlin
       vi .bashrc
       export PATH=$PATH:/home/try/.sdkman/candidates/kotlin/current/bin
	  ```
    
      You might need to reboot.

      **INCASE this does not work:**
      copy lib folder's contents to /usr/lib and bin folder's contents to /usr/bin
      ```
	  cd /home/try/.sdkman/candidates/kotlin/current/bin
      cp * /usr/bin
      cd /home/try/.sdkman/candidates/kotlin/current/lib
      cp * /usr/lib
	  ```
    * For R: ```sudo apt-get install littler```
    * For SWIFT
    
      Install clang: ```sudo apt-get —assume-yes install clang```
      
      Download Swift: https://swift.org/download/#releases ```i.e wget …```
      
      Extract: ```tar zxf swift-4.0-RELEASE-ubuntu14.04.tar.gz```
      
      Add the bin directory to path:
	  ```
      sudo mkdir /usr/local/swift
      cd ~/swift-4.0-RELEASE-ubuntu14.04/usr
      cp -r * /usr/local/swift
      vi ~/.bashrc
      export PATH=$PATH:/home/try/.sdkman/candidates/kotlin/current/bin
      ```
      Change the permissions:
	  ```
	  cd /usr/local/swift && sudo chmod -R o+r *
      ```

### Removing files from /tmp periodically
1. We will use [tmpreaper](http://manpages.ubuntu.com/manpages/trusty/man8/tmpreaper.8.html).
```
sudo apt-get install tmpreaper
crontab -e
*/5 * * * * /usr/sbin/tmpreaper 2m /tmp
```

  *  Tmpreaper has been setup to check in /tmp directory every 5 minutes and remove files that were last accessed 2 minutes ago.
  
### Monit for system monitoring
1. Install:  ```sudo apt-get install monit```
2. Open configuration file: ```sudo vi /etc/monit/monitrc```
3. To enable web interface:
  *  Search for "httpd" and replace it with the following:
  ```
    set httpd port 2812 and
    use address 0.0.0.0  # only accept connection from localhost
    allow 0.0.0.0/0.0.0.0        # allow localhost to connect to the server and
    allow admin:webcomp      # require user ‘admin’' with password 'webcomp'
  ```
4. Restart: ```sudo service monit restart```
5. Now you can go to http://your_server_ip_address:2812 to view the monitoring status.
6. To enable email alert:
  * Edit the configuration file again and add the following line to receive notification emails. ***NOTE:*** Replace youremail @ email.com with your valid email address where you want to receive system notification.
  ```
  set mailserver localhost
  set alert youremail@email.com not on {pid, ppid, instance, action, connection, exec, nonexist}
  ```
7. In order to support email, make sure you do the following:
  * Install postfix: ```sudo apt-get install mailutils```
  * Choose 'Internet Site' while installing postfix.
  * Try sending a test email. Type the following on terminal: ```echo "My message" | mail -s subject youremail@email.com```
  * Check your email. You should have received the email. If yes, then configuration is alright and you will receive emails from Monit.
  * Restart monit: ```sudo service monit restart```
8. Add the following to the monitrc file to monitor different statuses. ***NOTE:*** Replace *try* with the correct username in your case.
  * To monitor nginx:
  ```
  check process nginx with pidfile /var/run/nginx.pid
      start program = "/etc/init.d/nginx start"
      stop program = "/etc/init.d/nginx stop"
      if does not exist then restart
      if failed host 108.61.117.85 port 80 protocol http
          and request "/index.html"
          with timeout 25 seconds
          for 4 times within 4 cycles
          then restart
      if totalmem > 80% for 2 cycles then restart
      if cpu > 80% for 2 cycles then restart
      if 3 restarts within 3 cycles then alert
  ```
  * To monitor compiler API:
  ```
  check process compiler_api with pidfile /home/try/gunicorn
          start program = "/sbin/start compilerapi"
          stop program = "/sbin/stop compilerapi"
          if does not exist then restart
          if totalmem > 80% for 2 cycles then restart
          if cpu > 80% for 2 cycles then restart
          if 2 restarts within 2 cycles then alert
  ```
  * To monitor the terminal backend application:
  ```
  check process xterm with pidfile /home/try/xterm.pid
          start program = "/bin/bash -c 'cd /home/try && python app.py'"
          as uid "try" and gid "try"
          stop program = "/bin/bash -c 'pkill -9 python'"
          as uid 0 and gid 0
          if does not exist then restart
          if totalmem > 80% for 2 cycles then restart
          if cpu > 80% for 2 cycles then restart
          if 2 restarts within 2 cycles then alert
  ```
  * To monitor disk space:
  ```
  check filesystem rootfs with path / #Alert if low on disk space.
      if space usage > 90% then alert
  ```
9. Restart monit: ```sudo service monit restart```

### Misc. Setup

1. If you get an error while trying to run C programs, an error similar to command not found or file not found or / cannot be specified in the command, then the environment variable has not been setup properly. In such case where the Environment Variable does not change due to the sandbox, make change to the system-wide bashrc file:
  * Open the file: ```sudo vi /etc/bash.bashrc```
  * And put: 
  ```
  alias sh="rbash"
  alias bash="rbash"
  PATH="$PATH:/home/try:/tmp:/usr/local/swift/bin"
  ```
  * Reboot the system.
2. Copy 10minkill.sh and limit.sh to */home/username* directory. 
3. Give execution permission to the scripts:
    ```
	chmod +x limit.sh
	chmod +x 10minkill.sh
	```
4. Add them to crontab
    ```
	crontab -e
	* * * * * /home/your_username/limit.sh > /dev/null
	*/5 * * * * /home/your_username/10minkill.sh > /dev/null
	```
---
 
## RUN

**Open http://your_IP_address/C.html once all things above are done.**



  
